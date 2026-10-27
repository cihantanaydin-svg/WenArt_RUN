"""26 Oct 2026 (real06; every real06 run: the judge's "the view out the window is a flat grey void", the GPU test
``test_sky_and_window_pulls_reach_their_targets[real06]``: median pane saturation 0.063 < 0.065; Argus: "inferred
trees: placed 0 of 3 (74 candidates; ... window 67 ...)"). Three general rules of the site, tested on the CPU:

- ``site.place_trees``: the strict pass of before, then the framing pass (a grid over the plot, the window rule only
  near the facade: the crown keeps its distance from the window's light and off its straight view, the trees picked by
  the windows that see them) and the beyond-plot pass (a neighbour's tree just beyond the plot edge, inferred context).
  On small plots with windows on every side the old rule placed 0; the new one places the planned trees, seen from
  the windows, and logs every pass. real06's inputs of the run (``tests/fixtures/real06_site_trees_20261026.json``)
  reproduce the run's "placed 0 of 3" in the strict pass and now place 3 of 3.
- ``site.horizon_context`` / ``context_parts`` / ``build_context``: tree groups at the horizon around the site, outside
  the plot, the near ground and the exterior cameras' reach, with open fields between them; one mesh object that casts
  no shadow and lights nothing.
- ``vegetation.lawn_material``: the lawn keeps its colour on the camera's paths through a window pane (Light Path
  'Diffuse Depth' 0), grey only in the light it bounces; ``vegetation.context_material``: the context crowns' leaf
  texture.
Each test fails on a623f66 (no framing or beyond-plot pass, no context, the lawn grey through every pane)."""
from __future__ import annotations

import json
import math
import sys
import types
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender import site as S
from wenart.blender import vegetation as VG

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_site_trees_20261026.json"
CFG = S.TREE_FRAMING


def _real06():
    d = json.loads(REAL06.read_text(encoding="utf-8"))
    windows = [{"centre": tuple(w["centre"]), "outward": tuple(w["outward"]), "half_t": w["half_t"],
                "opening": {"id": w["id"], "width": w["width"]}} for w in d["windows"]]
    return d, windows


def _box_building(w: float, d: float, step: float = 2.5, width: float = 1.2):
    """A ``w`` x ``d`` m box with a window every ``step`` m on all four facades (the windows of the strict pass's
    bands cover every side)."""
    outline = [(0.0, 0.0), (w, 0.0), (w, d), (0.0, d)]
    windows = []
    for a, b, out in (((0, 0), (w, 0), (0, -1)), ((w, 0), (w, d), (1, 0)), ((w, d), (0, d), (0, 1)),
                      ((0, d), (0, 0), (-1, 0))):
        length = math.dist(a, b)
        k = max(1, int(length // step))
        for j in range(k):
            t = (j + 0.5) / k
            c = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            windows.append({"centre": c, "outward": out, "half_t": 0.15,
                            "opening": {"id": f"win_{len(windows) + 1:02d}", "width": width}})
    return outline, windows


def _old_rule_places(plot, outline, paths, windows, main):
    """The trees the rule of a623f66 placed (its first pass and its relaxed pass: the window band 8 m / 2 m, then
    4 m / 1 m, on the one ring ``tree_inset`` inside the plot), replayed with ``window_zone`` (no view zone)."""
    out = 0
    for reach, side in ((S.INFERRED["tree_window_reach"], S.INFERRED["tree_window_side"]), (4.0, 1.0)):
        stats = {}
        saved = dict(S.INFERRED)
        try:
            S.INFERRED.update(tree_window_reach=reach, tree_window_side=side)
            S.place_trees(plot, outline, paths, windows, main, 3, stats=stats)
        finally:
            S.INFERRED.update(saved)
        out = max(out, stats["placed_first"])
    return out


def _assert_tree_keeps_the_windows(t, windows):
    r = t["size"][0] / 2.0
    for w in windows:
        assert S.window_zone(t["center"], w, r, CFG["light_m"], CFG["side_m"], CFG["view_m"]) is None, (t, w)
        (cx, cy), (ox, oy) = w["centre"], w["outward"]
        dx, dy = t["center"][0] - cx, t["center"][1] - cy
        along, side = dx * ox + dy * oy, abs(dx * -oy + dy * ox)
        if along > 0 and side < w["opening"]["width"] / 2.0 + r:               # on the window's straight view
            assert along - r >= CFG["view_m"] - 1e-6
        if along > 0 and side < w["opening"]["width"] / 2.0 + CFG["side_m"] + r:
            assert along - r >= CFG["light_m"] - 1e-6                           # its light


# --------------------------------------------------------------------------
# The tree rule
# --------------------------------------------------------------------------

def test_real06_strict_pass_reproduces_the_run_and_the_new_passes_place_three_trees_seen_from_the_windows():
    """real06 (runs/20261026-183115-full): the strict pass gives exactly the run's numbers (74 candidates; building 1,
    path 15, sightline 36, window 67, front 27: 0 placed); the framing pass places two trees beside the windows'
    straight views 5.9 / 6.0 m from the nearest window that sees them, the beyond-plot pass one neighbour's tree 3 m
    beyond the back edge of the plot, 9.1 m from the back windows; 18 of the 29 windows see a tree."""
    d, windows = _real06()
    assert "placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 67, front 27" \
        in d["run_warning"]
    stats = {}
    trees = S.place_trees(d["plot"], d["outline"], d["paths"], windows, d["main"], 3, stats=stats)
    assert stats["candidates"] == 74 and stats["placed_first"] == 0
    assert stats["removed"] == {"building": 1, "path": 15, "sightline": 36, "window": 67, "front": 27}
    assert _old_rule_places(d["plot"], d["outline"], d["paths"], windows, d["main"]) == 0
    assert len(trees) == 3 and stats["placed"] == 3 and stats["relaxed"] and stats["beyond"]
    assert [t["placement"] for t in trees] == ["framing", "framing", "beyond_plot"]
    assert [p["name"] for p in stats["passes"]] == list(S.TREE_PASSES)
    assert [p["placed"] for p in stats["passes"]] == [0, 2, 1]
    for p in stats["passes"]:                                       # every pass logs its candidates and removals
        assert p["ran"] and p["candidates"] > 0 and set(p["removed"]) == set(S.TREE_FILTERS)
    plot = [tuple(p) for p in d["plot"]]
    for t in trees:
        assert t["inferred"] and t["seen_from"] and t["window_distance_m"] >= 4.25
        _assert_tree_keeps_the_windows(t, windows)
        assert geom2d.distance_to_polygon_edges(t["center"], d["outline"]) >= S.INFERRED["tree_from_building"]
        assert -t["center"][1] <= max(-p[1] for p in d["outline"]) - S.INFERRED["front_zone_extra"]  # no front garden
    framing = [t for t in trees if t["placement"] == "framing"]
    assert all(G.point_in_polygon(tuple(t["center"]), plot) for t in framing)
    assert sorted(round(t["window_distance_m"], 1) for t in framing) == [5.9, 6.0]
    [beyond] = [t for t in trees if t["placement"] == "beyond_plot"]
    assert beyond["context"] and not G.point_in_polygon(tuple(beyond["center"]), plot)
    assert geom2d.distance_to_polygon_edges(beyond["center"], plot) == pytest.approx(CFG["beyond_m"], abs=0.01)
    assert beyond["size"] == [CFG["beyond_crown"]] * 2 and len(beyond["seen_from"]) == 9
    assert stats["windows_seeing"] == 18 and stats["windows"] == 29
    assert all(math.dist(a["center"], b["center"]) >= S.INFERRED["tree_spacing"]
               for i, a in enumerate(trees) for b in trees[i + 1:])
    entry, warning = S.trees_record(stats)
    assert warning is None and entry["value"] == 3
    assert entry["reason"].startswith("inferred trees: placed 3 of 3 (74 candidates; removed by building 1, path 15, "
                                      "sightline 36, window 67, front 27; most by window")
    assert "the framing pass (the window rule near the facade only) placed 2 of" in entry["reason"]
    assert "the beyond-plot pass (a neighbour's garden) placed 1 of" in entry["reason"]
    assert "seen from 18 of 29 windows" in entry["reason"]


@pytest.mark.parametrize("size", [(10.0, 8.0), (14.0, 9.0), (8.0, 8.0)])
def test_small_plots_with_windows_on_every_side_get_their_trees_seen_from_the_windows(size):
    """A box with a 1.2 m window every 2.5 m on every facade on its inferred plot (6 m margin): the rule of a623f66
    placed no tree (every ring candidate in a window band); now the planned three stand where no window loses its light
    or its straight view, each seen from a window, inside the plot or just beyond it (a neighbour's tree), 6 m apart."""
    outline, windows = _box_building(*size)
    plot = S.inferred_plot(outline)
    main = {"direction": (0.0, -1.0)}
    assert _old_rule_places(plot, outline, [], windows, main) == 0
    stats = {}
    trees = S.place_trees(plot, outline, [], windows, main, 3, stats=stats)
    assert len(trees) == 3 and stats["placed_first"] == 0 and stats["placed"] == 3
    assert stats["placed_relaxed"] + stats["placed_beyond"] == 3
    grown = geom2d.offset_polygon(plot, -(CFG["beyond_m"] + CFG["beyond_row_m"] * (CFG["beyond_rows"] - 1)) - 0.01)
    for t in trees:
        assert t["seen_from"] and t["placement"] in ("framing", "beyond_plot")
        _assert_tree_keeps_the_windows(t, windows)
        assert G.point_in_polygon(tuple(t["center"]), grown)                 # in the plot or just beyond it
        front_edge = max(-p[1] for p in outline)
        assert -t["center"][1] <= front_edge - S.INFERRED["front_zone_extra"] + 1e-6       # never the front garden
    assert all(math.dist(a["center"], b["center"]) >= S.INFERRED["tree_spacing"]
               for i, a in enumerate(trees) for b in trees[i + 1:])
    assert len({w for t in trees for w in t["seen_from"]}) == stats["windows_seeing"] >= 3


def test_the_beyond_plot_pass_keeps_clear_of_the_paths_way_on():
    """A tree beyond the plot edge never stands on the continuation of a path (the street or the gate it leads to):
    ``path_corridor`` continues the path along its outward direction; without the corridor a tree would stand right in
    line with the back path."""
    outline, windows = _box_building(10.0, 8.0)
    plot = S.inferred_plot(outline)
    back = {"polygon": [(4.4, 8.3), (5.6, 8.3), (5.6, 14.05), (4.4, 14.05)], "outward": (0.0, 1.0)}
    corridor = S.path_corridor(back, 8.0)
    assert G.point_in_polygon((5.0, 18.0), corridor) and not G.point_in_polygon((5.0, 9.0 + 14.0), corridor)
    assert max(p[1] for p in corridor) == pytest.approx(22.05)
    stats = {}
    trees = S.place_trees(plot, outline, [back], windows, {"direction": (0.0, -1.0)}, 3, stats=stats)
    for t in [t for t in trees if t["placement"] == "beyond_plot"]:
        r = t["size"][0] / 2.0
        assert not G.point_in_polygon(tuple(t["center"]), corridor)
        assert geom2d.distance_to_polygon_edges(t["center"], corridor) >= S.INFERRED["tree_from_path"] - 1e-6
        assert r > 0
    beyond = next(p for p in stats["passes"] if p["name"] == "beyond_plot")
    assert beyond["ran"] and beyond["removed"]["path"] > 0


def test_an_open_plot_keeps_the_strict_pass_and_runs_no_other():
    """A plot with room (no windows in the way) keeps the trees of the strict pass exactly as before; the framing and
    beyond-plot passes are logged as not run."""
    outline = [(0.0, 0.0), (10.0, 0.0), (10.0, 8.0), (0.0, 8.0)]
    plot = S.inferred_plot(outline)
    stats = {}
    trees = S.place_trees(plot, outline, [], [], {"direction": (0.0, -1.0)}, 2, stats=stats)
    assert len(trees) == 2 and all(t["placement"] == "strict" for t in trees)
    assert [(p["name"], p["ran"]) for p in stats["passes"]] == [("strict", True), ("framing", False),
                                                               ("beyond_plot", False)]
    assert not stats["relaxed"] and not stats["beyond"]
    entry, warning = S.trees_record(stats)
    assert warning is None and "framing pass" not in entry["reason"] and "placed 2 of 2" in entry["reason"]


def test_window_zone_and_windows_seeing():
    """The near zones of a 1.2 m window facing -y at the origin with a 1.75 m crown: the light zone reaches 2.5 m +
    the crown out and 1 m + the crown beside, the view strip 6 m + the crown out; a tree is seen from the window only
    in front of it, within 55 degrees and 25 m, with no wall in between."""
    w = {"centre": (0.0, 0.0), "outward": (0.0, -1.0), "half_t": 0.15, "opening": {"id": "w1", "width": 1.2}}
    r = 1.75
    zone = lambda p: S.window_zone(p, w, r, CFG["light_m"], CFG["side_m"], CFG["view_m"])  # noqa: E731
    assert zone((0.0, -4.0)) == "light" and zone((3.2, -4.0)) == "light" and zone((3.4, -4.0)) is None
    assert zone((0.0, -7.0)) == "view" and zone((2.3, -7.0)) == "view" and zone((2.4, -7.0)) is None
    assert zone((0.0, -7.8)) is None and zone((0.0, 1.0)) is None
    box = [(-5.0, 0.0), (5.0, 0.0), (5.0, 6.0), (-5.0, 6.0)]
    assert S.windows_seeing((2.0, -6.0), [w], box) == [("w1", pytest.approx(math.hypot(2.0, 5.8), abs=0.001))]
    assert S.windows_seeing((9.0, -1.0), [w], box) == []                         # 80 degrees off the axis
    assert S.windows_seeing((0.0, -30.0), [w], box) == []                        # beyond 25 m
    behind = [(-5.0, 0.0), (5.0, 0.0), (5.0, 6.0), (2.0, 6.0), (2.0, -8.0), (1.0, -8.0), (1.0, 6.0), (-5.0, 6.0)]
    assert S.windows_seeing((4.0, -6.0), [w], behind) == []                      # a wing in between


def test_inferred_site_lists_the_passes_and_the_seen_windows():
    """``inferred_site`` (through ``site_plan``) of a small box with windows on all sides: the trees, their
    ``placement`` and ``seen_from``, and the ``assumed`` entry naming the passes; no warning when all are placed."""
    pts = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls = [{"id": f"w{i}", "level_id": "L0", "start": list(pts[i]), "end": list(pts[(i + 1) % 4]),
              "thickness": 0.25, "exterior": True} for i in range(4)]
    openings = []
    for i, wall in enumerate(walls):
        (ax, ay), (bx, by) = wall["start"], wall["end"]
        for k, t in enumerate((0.25, 0.75)):
            openings.append({"id": f"win_{i}_{k}", "type": "window", "level_id": "L0", "wall_id": wall["id"],
                             "center": [ax + (bx - ax) * t, ay + (by - ay) * t], "width": 1.2, "height": 1.2,
                             "sill_height": 0.9})
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "walls": walls, "openings": openings,
         "rooms": [], "slabs": [], "site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.0,
                                                                                         "method": "vector"}}]}},
         "facade": {}}
    outline, _ = geom2d.wall_outline(b["walls"])
    plan = S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none", "trees": 3})
    inf = plan["inferred"]
    windows = S.outer_openings(b, b["levels"], outline, None, kinds=("window",))
    assert len(windows) == 8
    assert len(inf["trees"]) == 3 and not [w for w in plan["warnings"] if w.startswith("inferred trees")]
    assert all(t["seen_from"] and t["placement"] in S.TREE_PASSES for t in inf["trees"])
    [entry] = [a for a in plan["assumed"] if a["field"] == "trees"]
    assert entry["reason"].startswith("inferred trees: placed 3 of 3") and "seen from" in entry["reason"]
    assert [t["id"] for t in plan["trees"]] == [t["id"] for t in inf["trees"]]      # they join the site's trees


# --------------------------------------------------------------------------
# The horizon context
# --------------------------------------------------------------------------

def _angular_cover(ctx, ring=None) -> int:
    cx, cy = ctx["centre"]
    cover = [0] * 360
    for t in ctx["trees"]:
        if ring and t["ring"] != ring:
            continue
        d = math.hypot(t["center"][0] - cx, t["center"][1] - cy)
        a = math.degrees(math.atan2(t["center"][1] - cy, t["center"][0] - cx))
        half = math.degrees(math.atan2(t["width"] / 2.0, d))
        for k in range(int(math.floor(a - half)), int(math.ceil(a + half)) + 1):
            cover[k % 360] = 1
    return sum(cover)


def test_real06_horizon_context_rings_stay_outside_the_plot_the_near_ground_and_the_cameras_reach():
    """real06 (fixture): the context's trees stand outside the plot, outside the near ground (the haze's clear hole)
    and beyond the exterior cameras' reach (4.5 x the building's radius + 10 m from its centre: the run's cameras
    stood 13-25 m from it); the near groups are 8-14 m trees at 49-92 m, the far line 12-20 m trees from 350 m; from a
    ground-floor eye their tops stand 1-14 degrees over the horizon (green in every window's view of the horizon), and
    open fields keep the horizon itself in view in some directions; the build repeats (seeded)."""
    d, _w = _real06()
    terrain = dict(d["terrain"], warnings=[], assumed=[])
    ctx = S.horizon_context(d["outline"], d["near_extent"], terrain, d["climate"], d["height_m"])
    again = S.horizon_context(d["outline"], d["near_extent"], terrain, d["climate"], d["height_m"])
    assert ctx == again and ctx["inferred"] and ctx["count"] == len(ctx["trees"]) > 50
    assert [r["name"] for r in ctx["rings"]] == ["near", "far"] and all(r["count"] > 10 for r in ctx["rings"])
    clear = S.context_clear_radius(d["outline"], d["height_m"])
    assert clear == ctx["clear_m"] and 45.0 < clear < 60.0
    cx, cy = ctx["centre"]
    run_cameras = [(13.225, -7.4862), (13.225, 22.0612), (-4.375, 22.0612), (-4.625, -7.9192), (-8.7964, 28.8268),
                   (4.425, -9.125)]
    assert max(math.hypot(x - cx, y - cy) for x, y in run_cameras) < clear - 10.0
    plot = [tuple(p) for p in d["plot"]]
    nx0, ny0, nx1, ny1 = G.bbox([tuple(p) for p in d["near_extent"]])
    species = {n for n, _w in S.CONTEXT_SPECIES["mediterranean"]}
    for t in ctx["trees"]:
        x, y = t["center"]
        assert not G.point_in_polygon((x, y), plot)
        assert not (nx0 <= x <= nx1 and ny0 <= y <= ny1)                         # beyond the near ground
        assert max(abs(x - cx), abs(y - cy)) >= clear - 3.0 - 8.0               # the jitter of the rows
        assert t["species"] in species and t["z"] == -0.5
        lo, hi = S.HORIZON_CONTEXT["rings"][0 if t["ring"] == "near" else 1]["height_m"]
        assert lo <= t["height"] <= hi and 0 < t["crown_h"] <= t["height"]
        eye = -0.5 + 1.75
        elevation = math.degrees(math.atan2(t["z"] + t["height"] - eye, math.hypot(x - cx, y - cy)))
        assert 0.5 < elevation < 15.0
    assert 150 <= _angular_cover(ctx, "near") <= 330
    assert 300 <= _angular_cover(ctx) <= 350                                   # open fields: the horizon shows
    assert "inferred context" in ctx["reason"]


def _context_faces(trees) -> int:
    c = S.HORIZON_CONTEXT
    return sum(8 + c["blob_segments"] * c["blob_rings"] * c["blobs"][t["shape"]] for t in trees)


def test_context_parts_are_lumpy_crowns_on_trunks_with_a_material_per_species():
    """``context_parts``: per tree a 6-sided tapered trunk (8 faces) and a crown of foliage masses (27 Oct 2026: the
    judge saw lollipops in a 60-face ball on a stick), each a lumpy blob, never a smooth ball (the radius varies around
    every ring); ``slots`` name the species' leaf material or the bark (last)."""
    d, _w = _real06()
    terrain = dict(d["terrain"], warnings=[], assumed=[])
    ctx = S.horizon_context(d["outline"], d["near_extent"], terrain, d["climate"], d["height_m"])
    parts = S.context_parts(ctx)
    n = ctx["count"]
    assert len(parts["faces"]) == _context_faces(ctx["trees"]) == len(parts["slots"])
    assert 250 <= parts["faces_per_tree"] <= 600                     # a cluster, not a 68-face lollipop
    assert parts["materials"][-1] == "bark" and sorted(parts["materials"][:-1]) == sorted(ctx["species"])
    assert set(parts["slots"]) == set(range(len(parts["materials"])))
    assert sum(1 for s in parts["slots"] if s == len(parts["materials"]) - 1) == 8 * n
    # the masses of a crown: a core and the others around it, inside the crown's width; stacked for a cypress
    blobs = S.crown_cluster((0.0, 0.0, 6.0), 3.0, 2.5, "round", 5)
    assert len(blobs) == S.HORIZON_CONTEXT["blobs"]["round"] and blobs[0]["rx"] > max(b["rx"] for b in blobs[1:])
    assert all(math.hypot(b["center"][0], b["center"][1]) <= 3.0 for b in blobs)
    col = S.crown_cluster((0.0, 0.0, 6.0), 0.8, 4.0, "columnar", 5)
    assert col[-1]["center"][2] > col[1]["center"][2] and col[-1]["rx"] <= col[1]["rx"]
    v, f = S.tapered_trunk(0.0, 0.0, 0.0, 5.0, 0.3, 0.15, 6)
    assert len(f) == 8 and max(math.hypot(p[0], p[1]) for p in v if p[2] == 5.0) == pytest.approx(0.15)
    assert all(0 <= i < len(parts["verts"]) for f in parts["faces"] for i in f)
    # one crown: the radii of a middle ring vary (lumps), the crown stands over its ground point
    t = ctx["trees"][0]
    v, f = S._context_crown((0.0, 0.0, 5.0), 3.0, 2.0, "round", 7, 10, 6, S.HORIZON_CONTEXT["lump"])
    radii = [math.hypot(p[0], p[1]) for p in v[1 + 2 * 10:1 + 3 * 10]]
    assert max(radii) - min(radii) > 0.2 and len(f) == 60
    cone, _f = S._context_crown((0.0, 0.0, 5.0), 3.0, 2.0, "conical", 7, 10, 6, 0.0)
    low, high = cone[1 + 1 * 10], cone[1 + 4 * 10]
    assert math.hypot(low[0], low[1]) > math.hypot(high[0], high[1])            # a cone narrows to its top
    zs = [p[2] for p in parts["verts"]]
    assert min(zs) == pytest.approx(t["z"] - S.HORIZON_CONTEXT["sink_m"], abs=0.5)


def test_site_plan_carries_the_context_only_with_the_sky_lever_and_a_full_site(monkeypatch):
    """``site_plan``: the context with ``site: full`` and the ``sky`` lever (an ``assumed`` entry lists it); none for
    ``site: ground`` or the ``base`` site variant."""
    pts = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls = [{"id": f"w{i}", "level_id": "L0", "start": list(pts[i]), "end": list(pts[(i + 1) % 4]),
              "thickness": 0.25, "exterior": True} for i in range(4)]
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "walls": walls, "openings": [],
         "rooms": [], "slabs": [], "site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.0,
                                                                                         "method": "vector"}}]}},
         "facade": {}}
    outline, _ = geom2d.wall_outline(b["walls"])
    monkeypatch.delenv(S.SITE_VARIANT_ENV, raising=False)
    plan = S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none", "trees": 2})
    ctx = plan["context"]
    assert ctx and ctx["count"] > 0 and ctx["climate"] == plan["climate"]["climate"]
    [entry] = [a for a in plan["assumed"] if a["field"] == "context"]
    assert entry["value"] == ctx["count"] and "inferred context" in entry["reason"]
    assert S.building_height(b["levels"]) == pytest.approx(5.8)
    assert S.site_plan(b, b["levels"], outline, "ground")["context"] is None
    monkeypatch.setenv(S.SITE_VARIANT_ENV, "base")
    assert S.site_plan(b, b["levels"], outline, "full", options={"path": False, "fence": "none"})["context"] is None


# --------------------------------------------------------------------------
# The bpy parts with a fake bpy: the lawn's own colour through a pane, the context material and object
# --------------------------------------------------------------------------

class _Sock:
    def __init__(self, node, key):
        self.node, self.key, self.default_value = node, key, None

    @property
    def links(self):
        return [ln for ln in self.node.tree.links if ln.to_socket is self]


class _Socks:
    def __init__(self, node):
        self.node, self.d = node, {}

    def __getitem__(self, key):
        if key not in self.d:
            self.d[key] = _Sock(self.node, key)
        return self.d[key]

    def __contains__(self, key):
        return True


class _Link:
    def __init__(self, a, b):
        self.from_socket, self.to_socket = a, b


class _Links(list):
    def new(self, a, b):
        self.append(_Link(a, b))
        return self[-1]

    def remove(self, link):
        list.remove(self, link)


class _Node:
    def __init__(self, tree, idname):
        self.tree, self.bl_idname, self.operation, self.image = tree, idname, None, None
        self.inputs, self.outputs = _Socks(self), _Socks(self)
        self.color_ramp = types.SimpleNamespace(elements=[types.SimpleNamespace(color=None),
                                                          types.SimpleNamespace(color=None)])


class _Nodes(list):
    def __init__(self, tree):
        super().__init__()
        self.tree = tree

    def new(self, idname):
        self.append(_Node(self.tree, idname))
        return self[-1]

    def remove(self, node):
        list.remove(self, node)

    def get(self, name):
        return None


class _Tree:
    def __init__(self):
        self.links = _Links()
        self.nodes = _Nodes(self)


class _Mat(dict):
    def __init__(self, name):
        super().__init__()
        self.name, self.use_nodes, self.node_tree = name, False, _Tree()


@pytest.fixture()
def fake_bpy(monkeypatch):
    mats: dict = {}

    def new(name):
        mats[name] = _Mat(name)
        return mats[name]
    bpy = types.SimpleNamespace(data=types.SimpleNamespace(
        materials=types.SimpleNamespace(get=mats.get, new=new),
        images=types.SimpleNamespace(load=lambda path, check_existing=True: types.SimpleNamespace(filepath=path)),
        objects=types.SimpleNamespace(remove=lambda ob, do_unlink=True: None)))
    monkeypatch.setitem(sys.modules, "bpy", bpy)
    return bpy


def _edges(tree):
    return [(ln.from_socket.node.bl_idname, ln.from_socket.node.operation, ln.from_socket.key,
             ln.to_socket.node.bl_idname, ln.to_socket.node.operation, ln.to_socket.key) for ln in tree.links]


def test_lawn_keeps_its_colour_through_a_window_pane_and_greys_only_its_bounced_light(fake_bpy):
    """real06's grey void: the lawn turned 75 % grey for every ray but the camera's, and the camera's ray through a
    pane is a transmission ray after the glass. The grey factor is now LAWN_BOUNCE_DESAT x min(Diffuse Depth, 1): 0 on
    the camera's paths through the glass (and in a mirror), LAWN_BOUNCE_DESAT on the light the lawn bounces onto the
    walls and into the rooms; 'Is Camera Ray' no longer decides it."""
    mat = _Mat("lawn")
    tree = mat.node_tree
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.1, 0.3, 0.1, 1.0)
    rec = VG.lawn_material(mat)
    assert rec["applied"] and rec["bounce_desaturation"] == VG.LAWN_BOUNCE_DESAT
    assert rec["own_colour_rays"] == "Diffuse Depth 0" and VG.LAWN_OWN_COLOUR_RAYS == "Diffuse Depth"
    edges = _edges(tree)
    assert not [e for e in edges if e[2] == "Is Camera Ray"]
    assert ("ShaderNodeLightPath", None, "Diffuse Depth", "ShaderNodeMath", "MINIMUM", 0) in edges
    mn = next(n for n in tree.nodes if n.operation == "MINIMUM")
    mul = next(n for n in tree.nodes if n.operation == "MULTIPLY")
    assert mn.inputs[1].default_value == 1.0 and mul.inputs[1].default_value == VG.LAWN_BOUNCE_DESAT
    assert ("ShaderNodeMath", "MINIMUM", 0, "ShaderNodeMath", "MULTIPLY", 0) in edges
    assert ("ShaderNodeMath", "MULTIPLY", 0, "ShaderNodeMix", None, "Factor") in edges
    # the factor on the paths: camera through the pane (diffuse depth 0) -> own colour; a bounce -> grey share
    grey = lambda depth: VG.LAWN_BOUNCE_DESAT * min(depth, 1.0)                 # noqa: E731
    assert grey(0) == 0.0 and grey(1) == grey(3) == VG.LAWN_BOUNCE_DESAT
    assert ("ShaderNodeMix", None, 2, "ShaderNodeBsdfPrincipled", None, "Base Color") in edges


def test_context_material_is_an_opaque_leaf_texture(fake_bpy, monkeypatch):
    """``context_material``: an opaque Principled BSDF (no Alpha link) whose Base Color is the clump ramp of the
    species colour times a fine leafy grain and a coarse variation between trees (27 Oct 2026: procedural by default,
    the atlas tile read as a dot grid from 50 m), with a bump; with ``CONTEXT_LEAF["atlas"]`` the species' leaf atlas
    on the box UVs (a tile every CONTEXT_LEAF["tile_m"]). Cached by name."""
    monkeypatch.setattr(VG, "leaf_atlas", lambda species, *a, **k: {"id": "LeafSet027", "licence": "CC0",
                                                                   "files": {"albedo": "/x/LeafSet027_Color.jpg"}})
    mat = VG.context_material("cypress")
    assert mat.name == "veg_context_cypress" and VG.context_material("cypress") is mat
    edges = _edges(mat.node_tree)
    assert not [e for e in edges if e[5] == "Alpha"]
    assert ("ShaderNodeValToRGB", None, "Color", "ShaderNodeMix", None, 6) in edges           # the clumps x grain
    assert ("ShaderNodeTexNoise", None, "Fac", "ShaderNodeMapRange", None, "Value") in edges
    assert ("ShaderNodeMix", None, 2, "ShaderNodeBsdfPrincipled", None, "Base Color") in edges
    assert not [n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeTexImage"]       # no atlas by default
    assert ("ShaderNodeBump", None, "Normal", "ShaderNodeBsdfPrincipled", None, "Normal") in edges
    assert mat["wenart_leaf_texture"] == "procedural" and mat["wenart_atlas"] == ""
    monkeypatch.setitem(VG.CONTEXT_LEAF, "atlas", True)
    mat = VG.context_material("olive")
    edges = _edges(mat.node_tree)
    assert ("ShaderNodeTexCoord", None, "UV", "ShaderNodeMapping", None, "Vector") in edges
    assert ("ShaderNodeTexImage", None, "Color", "ShaderNodeMix", None, 6) in edges
    assert ("ShaderNodeMix", None, 2, "ShaderNodeBsdfPrincipled", None, "Base Color") in edges
    mapping = next(n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeMapping")
    assert mapping.inputs["Scale"].default_value[0] == pytest.approx(1.0 / VG.CONTEXT_LEAF["tile_m"])
    assert mat["wenart_atlas"] == "LeafSet027" and mat["wenart_leaf_texture"] == "atlas"


class _Ob(dict):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.smooth = False
        self.data = types.SimpleNamespace(shade_smooth=lambda: setattr(self, "smooth", True))
        for attr in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission",
                     "visible_volume_scatter", "visible_shadow"):
            setattr(self, attr, True)


def test_build_context_makes_one_object_that_casts_no_shadow_and_lights_nothing(fake_bpy, monkeypatch):
    """``build_context``: one ``context_trees`` object (kind ``site_decor``) with a material per species and the bark,
    smooth shaded, hidden from shadow, diffuse and volume rays (the room light, the exposure and the white point stay as
    before) and seen by the camera, through a pane and in reflections; its manifest entry names the method, the atlas
    and the reason; a failure builds nothing and says why."""
    from wenart.blender import common

    made = {}

    def new_mesh_object(name, verts, faces, *, collection, wenart_id, kind, status, materials=(),
                        face_material_indices=None):
        made.update(name=name, faces=len(faces), kind=kind, materials=[m.name for m in materials],
                    slots=set(face_material_indices))
        made["ob"] = _Ob(name)
        return made["ob"]
    monkeypatch.setattr(common, "new_mesh_object", new_mesh_object)
    monkeypatch.setitem(VG.CONTEXT_LEAF, "atlas", True)
    monkeypatch.setattr(VG, "leaf_atlas", lambda species, *a, **k: {"id": "LeafSet027", "licence": "CC0",
                                                                   "files": {"albedo": "/x/c.jpg"}})
    d, _w = _real06()
    ctx = S.horizon_context(d["outline"], d["near_extent"], dict(d["terrain"]), d["climate"], d["height_m"])
    entries = []
    rec = S.build_context(ctx, None, lambda *a: entries.append(a))
    ob = made["ob"]
    assert rec["built"] and rec["trees"] == ctx["count"] and rec["faces"] == made["faces"] == _context_faces(ctx["trees"])
    assert made["name"] == S.CONTEXT_NAME and made["kind"] == "site_decor" and ob.smooth
    assert made["materials"][-1] == "veg_bark" and len(made["materials"]) == len(ctx["species"]) + 1
    assert not ob.visible_shadow and not ob.visible_diffuse and not ob.visible_volume_scatter
    assert ob.visible_camera and ob.visible_transmission and ob.visible_glossy
    assert rec["hidden_rays"] == list(S.CONTEXT_HIDDEN_RAYS) and rec["atlas"] == "LeafSet027"
    [(name, wid, kind, mat, status, extra)] = entries
    assert (name, wid, kind, mat, status) == ("context_trees", "context_trees", "site_decor", None, "assumed")
    assert extra["veg_method"] == "context" and extra["asset"] == "LeafSet027" and extra["licence"] == "CC0"
    assert extra["site_part"] == "context" and "inferred context" in extra["assumed"]["reason"]
    assert ob["wenart_veg_method"] == "context"
    # a failure: recorded, nothing built
    monkeypatch.setattr(S, "context_parts", lambda ctx: (_ for _ in ()).throw(ValueError("boom")))
    bad = S.build_context(ctx, None, lambda *a: entries.append(a))
    assert not bad["built"] and bad["error"] == "ValueError: boom" and len(entries) == 1


def test_the_context_is_credited_with_its_leaf_atlas(tmp_path):
    """``wenart.run.copy.vegetation_credits``: the context entry (``veg_method`` context, ``asset`` the atlas) is
    credited as the ambientCG CC0 leaf atlas."""
    from wenart.run import copy as C

    (tmp_path / "scene").mkdir()
    (tmp_path / "scene" / "scene_manifest.json").write_text(json.dumps({"objects": [
        {"name": "context_trees", "wenart_id": "context_trees", "veg_method": "context", "asset": "LeafSet027",
         "site_part": "context"}]}), encoding="utf-8")
    [row] = C.vegetation_credits(tmp_path)
    assert row["asset_id"] == "LeafSet027" and row["licence"] == "CC0" and row["pieces"] == [("context_trees",
                                                                                              "context")]


class _Tex:
    """An image: ``w`` x ``h`` RGB(A) texels from ``f(x, y) -> (r, g, b)``."""

    def __init__(self, w, h, f, channels=3):
        self.size, self.channels, self.alpha_mode = (w, h), channels, "NONE"
        self.pixels = [v for y in range(h) for x in range(w) for v in (*f(x, y), 1.0)[:channels]]


def test_a_leaf_texture_without_alpha_has_its_flat_background_keyed_out():
    """27 Oct 2026 (pod run 224516: a library tree rendered as a dotted disc): a leaf texture with no alpha on a flat
    white or black background gives that background (``image_background``); a texture that fills its frame (bark,
    foliage photographed edge to edge, a coloured background) gives none."""
    leaves_on_white = _Tex(32, 32, lambda x, y: (0.2, 0.5, 0.1) if 8 < x < 24 and 8 < y < 24 else (1.0, 1.0, 1.0))
    assert VG.image_background(leaves_on_white) == pytest.approx((1.0, 1.0, 1.0))
    leaves_on_black = _Tex(32, 32, lambda x, y: (0.2, 0.5, 0.1) if 8 < x < 24 else (0.0, 0.0, 0.0))
    assert VG.image_background(leaves_on_black) is None        # the leaves reach the border: no flat background
    black = _Tex(32, 32, lambda x, y: (0.2, 0.5, 0.1) if 6 < x < 26 and 6 < y < 26 else (0.01, 0.01, 0.01))
    assert VG.image_background(black) == pytest.approx((0.01, 0.01, 0.01))
    bark = _Tex(32, 32, lambda x, y: (0.3 + 0.01 * (x % 5), 0.2, 0.1))
    assert VG.image_background(bark) is None
    blue = _Tex(32, 32, lambda x, y: (0.2, 0.5, 0.1) if 8 < x < 24 and 8 < y < 24 else (0.2, 0.3, 0.9))
    assert VG.image_background(blue) is None                    # a coloured background is never keyed
    assert VG.image_background(None) is None


def test_the_scan_stands_before_a_generic_library_tree_near_the_cameras():
    """27 Oct 2026: near the cameras a library plant matched only by its crown or kind gives way to the species' Poly
    Haven scan when the assets hold it; a library model of the species itself stays; far from the cameras, without
    the scan or with the instances lever off, the library plant stays."""
    hero = lambda species: {"id": "island_tree_02"}            # noqa: E731
    none = lambda species: None                                 # noqa: E731
    generic, olive = {"id": "3dwh_x", "match": "kind"}, {"id": "3dwh_o", "match": "species"}
    assert VG.scan_first(generic, True, None, "olive", hero)
    assert not VG.scan_first(olive, True, None, "olive", hero)
    assert not VG.scan_first(generic, False, None, "olive", hero)
    assert not VG.scan_first(generic, True, None, "olive", none)
    assert not VG.scan_first(generic, True, {"instances": False}, "olive", hero)
