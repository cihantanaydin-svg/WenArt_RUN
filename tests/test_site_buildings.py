"""Several buildings on one plot (user request of 11 Oct 2026, real04; ``wenart/sheets/buildings.py``,
``wenart/blender/copies.py``).

real04's site plan (r14) holds two twin-villa blocks tilted 11 degrees, each drawn as two inserts of the block
``bina`` (one villa each: three sides of a 12.0 x 7.59 m rectangle), entrance markers (``G_BINA``) on their east side
and level marks (``BDK`` attributes) from 37 to 46 m. A synthetic copy of that layout (in centimetres) is read here:
two footprints of the plan's 15.2 x 12.0 m outline, the orientation from the entrance markers and the plan's door
swings, b2 18.6 m beside b1 and 3 m higher, ±0.00 = 43.00. Also: site labels whose estimated box lies outside their
tilted outline still name it (``24M2 HAVUZ``), a closed polyline whose last vertex repeats the first a little off is
read, the copy transforms move points and frames, site-plan marks are ground spot heights wherever they are."""
from __future__ import annotations

import json
import math
import textwrap

import pytest
from shapely.geometry import Polygon, box

from wenart.blender import copies as CP
from wenart.ingest.generic.model import Stroke
from wenart.sheets import buildings as BLD
from wenart.sheets import exterior as EX
from wenart.sheets import to_building as TB
from wenart.sheets.model import Ent, Region, Sheet, Txt

MPU = 0.01
TILT = 11.0


def rot(p, deg=TILT, about=(0.0, 0.0)):
    a = math.radians(deg)
    x, y = p[0] - about[0], p[1] - about[1]
    return (about[0] + math.cos(a) * x - math.sin(a) * y, about[1] + math.sin(a) * x + math.cos(a) * y)


def cm(p):
    return (p[0] / MPU, p[1] / MPU)


def unit(eid, x0, y0, x1, y1, open_side="top"):
    """One villa of a block (site metres, before the tilt): three sides of its rectangle, as the ``bina`` block."""
    c = {"bl": (x0, y0), "br": (x1, y0), "tr": (x1, y1), "tl": (x0, y1)}
    order = {"top": ["tr", "br", "bl", "tl"], "bottom": ["bl", "tl", "tr", "br"]}[open_side]
    pts = [cm(rot(c[k])) for k in order]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    st = Stroke(id=f"{eid}/0", kind="polyline", pts=pts, closed=False, layer="0", block="bina")
    return Ent(id=eid, kind="INSERT", layer="_P3_S_Duvar_Ç", box=(min(xs), min(ys), max(xs), max(ys)),
               strokes=[st], block="bina")


def marker(eid, p):
    q = cm(rot(p))
    st = Stroke(id=f"{eid}/0", kind="polyline", pts=[(q[0] - 30, q[1] - 30), (q[0] + 30, q[1] - 30),
                                                     (q[0], q[1] + 30)], closed=True, block="G_BINA")
    return Ent(id=eid, kind="INSERT", layer="_P10_İ_GirişBina", box=(q[0] - 30, q[1] - 30, q[0] + 30, q[1] + 30),
               strokes=[st], block="G_BINA")


def mark(tid, p, value):
    q = cm(rot(p))
    return Txt(id=tid, text=f"{value:.2f}", box=(q[0] - 20, q[1] - 10, q[0] + 20, q[1] + 10), height=20.0,
               evidence={"file": "site.dxf", "method": "vector", "confidence": 1.0, "attrib_tag": "BDK"})


def site_region() -> Region:
    """Two blocks 11.8 m wide along x (east = entrance side), 15.18 m along y, 18.58 m apart; entrance markers
    0.7 m east of each block; marks 40 west / 43 between / 46 east."""
    ents = []
    for k, x0 in enumerate((0.0, 18.58)):
        ents.append(unit(f"INSERT:B{k}a", x0, 0.0, x0 + 12.0, 7.59, "top"))
        ents.append(unit(f"INSERT:B{k}b", x0, 7.59, x0 + 12.0, 15.18, "bottom"))
        ents.append(marker(f"INSERT:G{k}a", (x0 + 12.7, 3.8)))
        ents.append(marker(f"INSERT:G{k}b", (x0 + 12.7, 11.4)))
    texts = [mark("ATTRIB:M1", (-3.0, 7.0), 40.0), mark("ATTRIB:M2", (13.5, 2.0), 43.0),
             mark("ATTRIB:M3", (13.5, 13.0), 43.0), mark("ATTRIB:M4", (32.0, 2.0), 46.0),
             mark("ATTRIB:M5", (32.0, 13.0), 46.0)]
    sheet = Sheet(id="s1", space="model", file="site.dxf", page=1)
    r = Region(id="r9", file="site.dxf", sheet=sheet, box=(0, 0, 1, 1), geometry_box=(0, 0, 1, 1), ents=ents,
               texts=texts, cls="site_plan", use="exterior")
    r.metres_per_unit = MPU
    return r


class Plan:
    """A registered plan: the twin block 15.2 x 12.0 m along x, its entrance doors on the +y side (arcs hinged on the
    outline at y = 12.0)."""
    id = "r16"
    metres_per_unit = 1.0
    transform_to_building = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    registration = {"method": "reference"}
    level = {"order": 0}

    def strokes(self):
        return [Stroke(id=f"arc{k}", kind="arc", pts=[(x, 12.0), (x + 0.9, 11.1)],
                       arc={"center": (x, 12.0), "radius": 0.9, "start_deg": 270, "end_deg": 360})
                for k, x in enumerate((3.0, 12.2))]


def outlines():
    return {"r16": box(0.0, 0.0, 15.18, 12.0)}


def test_two_twin_blocks_on_a_tilted_site_plan():
    r, warnings = site_region(), []
    copies = BLD.site_buildings(r, [Plan()], outlines(), warnings)
    assert [c["id"] for c in copies] == ["b1", "b2"] and copies[0]["reference"] and not copies[1]["reference"]
    for c in copies:
        assert c["orientation"] == "entrances" and c["plan_region"] == "r16"
        assert c["size_m"] == pytest.approx([15.18, 12.0], abs=0.02)
        assert len(c["entities"]) == 2 and all(e.startswith("INSERT:B") for e in c["entities"])
    b2 = copies[1]
    # the entrance side (site +x, east) is the plan's +y: b2 stands 18.58 m along the building's +y, 3 m higher
    assert b2["rotation_deg"] == pytest.approx(0.0, abs=0.05)
    assert b2["translate"] == pytest.approx([0.0, 18.58], abs=0.05)
    assert copies[0]["entrance_ground"] == 43.0 and b2["entrance_ground"] == 46.0 and b2["dz"] == 3.0
    # the site plan is registered through b1: its footprint lands on the plan outline
    assert r.registration["method"] == "site_buildings"
    assert Polygon(copies[0]["footprint"]).symmetric_difference(outlines()["r16"]).area < 0.5
    assert BLD.site_datum(copies, {"ground": [{"z": {"value": -3.15}}, {"z": {"value": 0.0}}]})["value"] == 43.0
    assert BLD.site_datum(copies, None)["value"] == 43.15                       # D3a: 0.15 m under the floor
    assert not [w for w in warnings if "ambiguous" in w]


def test_without_entrance_markers_the_orientation_is_listed_as_ambiguous():
    r = site_region()
    r.ents = [e for e in r.ents if e.block != "G_BINA"]
    warnings = []
    copies = BLD.site_buildings(r, [Plan()], outlines(), warnings)
    assert len(copies) == 2 and all(c["orientation"] == "ambiguous" for c in copies)
    assert copies[1]["dz"] == 0.0 and copies[1]["dz_note"]
    assert any("orientation ambiguous" in w for w in warnings)


def test_no_footprint_of_the_plans_size_gives_none():
    r = site_region()
    assert BLD.site_buildings(r, [Plan()], {"r16": box(0.0, 0.0, 20.0, 9.0)}, []) is None


def test_a_label_names_the_outline_next_to_it_and_its_written_area():
    pool = [cm(rot(p)) for p in ((0, 0), (8, 0), (8, 3), (0, 3))]
    zone = [cm(rot(p)) for p in ((-1, -1), (10.8, -1), (10.8, 3.8), (-1, 3.8))]
    setback = [cm(p) for p in ((-15, -15), (30, -15), (30, 20), (-15, 20))]
    closed = [(Polygon(p).area, Ent(id=i, kind="LWPOLYLINE", layer=None, box=(0, 0, 1, 1)), p)
              for i, p in (("pool", pool), ("zone", zone), ("setback", setback))]
    # the estimated label point lies 1 m beside the tilted pool, inside the zone and the setback outline
    t = Txt(id="MTEXT:1", text="24M2 HAVUZ", box=(*cm(rot((4.0, 4.4))), *cm(rot((4.0, 4.4)))), height=30.0)
    e, _ = EX.label_holder(t, closed, "pool", MPU)
    assert e.id == "pool"
    t2 = Txt(id="MTEXT:2", text="GÜNEŞLENME ALANI", box=(*cm(rot((9.5, 1.0))), *cm(rot((9.5, 1.0)))), height=30.0)
    e2, _ = EX.label_holder(t2, closed, "terrace", MPU)
    assert e2.id == "zone"                                     # the smallest near outline, never the setback
    assert EX.area_kind("GÜNEŞLENME ALANI") == "terrace" and EX.area_kind("24M2 HAVUZ") == "pool"


def test_a_closing_vertex_a_little_off_the_first_is_dropped():
    pts = [(716565.46, 4491056.66), (716623.07, 4490762.25), (717408.18, 4490915.86), (717350.34, 4491211.46),
           (716565.01, 4491056.57)]
    e = Ent(id="LWPOLYLINE:2F8CD", kind="LWPOLYLINE", layer="DERE_TARAMA", box=(0, 0, 1, 1),
            strokes=[Stroke(id="s", kind="polyline", pts=pts, closed=True)])
    got = EX._closed_pts(e)
    assert len(got) == 4 and Polygon(got).is_valid and Polygon(got).area * 1e-4 == pytest.approx(24.0, abs=0.1)
    assert not Polygon(pts).is_valid                          # the bow-tie the pools were lost to


def test_copy_transforms_and_a_frame_shift():
    c = {"id": "b2", "rotation_deg": 90.0, "translate": [10.0, 0.0], "dz": 3.0,
         "footprint": [[10, 0], [10, 5], [5, 5], [5, 0]]}
    assert CP.move_point(c, (1.0, 0.0)) == pytest.approx((10.0, 1.0))
    s = (2.0, 1.0)                                             # the pipeline frame: p' = p - s
    m = TB.moved_copy(c, s)
    p = (3.0, 4.0)
    want = CP.move_point(c, p)
    got = CP.move_point(m, (p[0] - s[0], p[1] - s[1]))
    assert got == pytest.approx((want[0] - s[0], want[1] - s[1]))
    assert m["footprint"][0] == pytest.approx([8.0, -1.0])


def test_the_site_view_sees_both_blocks_side_by_side():
    b = {"site": {"buildings": [{"id": "b1", "reference": True, "translate": [0, 0], "dz": 0.0, "footprint": []},
                                {"id": "b2", "reference": False, "rotation_deg": 0.0, "translate": [0.0, 18.6],
                                 "dz": 3.0, "footprint": [[0, 18.6], [15.2, 18.6], [15.2, 30.6], [0, 30.6]]}]}}
    outline = [(0, 0), (15.2, 0), (15.2, 12.0), (0, 12.0)]
    sv = CP.site_view(outline, b, (-3.0, 6.0))
    assert sv["position"][0] > 30.0 and abs(sv["position"][1] - sv["target"][1]) < 0.01      # from the gable side
    assert sv["position"][2] > sv["target"][2] + 10.0 and sv["lens_mm"] == CP.SITE_VIEW_LENS_MM
    assert CP.site_view(outline, {"site": {}}, (0.0, 3.0)) is None


def test_site_plan_marks_are_ground_wherever_they_stand():
    from wenart.levels import read as RD
    from wenart.levels.model import level_params

    building = {"project": {"datum": {"value": 43.0, "method": "derived", "evidence": [{}]}},
                "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
                "rooms": [{"id": "r1", "level_id": "L0", "polygon": [[0, 0], [10, 0], [10, 8], [0, 8]]}],
                "walls": [], "openings": []}
    params = level_params({})
    texts = [{"text": "46.00", "point": (5.0, 60.0), "level_id": "L0", "entity": "ATTRIB:1", "attrib_tag": "BDK",
              "evidence": {"file": "s.dxf", "method": "vector", "confidence": 1.0}, "site_ground": True},
             {"text": "40.00", "point": (5.0, -3.0), "level_id": "L0", "entity": "ATTRIB:2", "attrib_tag": "BDK",
              "evidence": {"file": "s.dxf", "method": "vector", "confidence": 1.0}, "site_ground": True}]
    res = RD.read_marks(texts, building, params)
    RD.classify(res["marks"], building, params)
    assert [(m["kind"], m["z"]) for m in res["marks"]] == [("ground_finished", 3.0), ("ground_finished", -3.0)]
    assert all(m.get("site_plan") for m in res["marks"])


# --------------------------------------------------------------------------
# The build: the levels fixture with a second block 20 m east, 1 m higher, and a pool
# --------------------------------------------------------------------------

def _two_blocks() -> dict:
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = M.infer_levels(F.building())
    ev = [dict(F.EV, entity="INSERT:bina")]
    site = b.setdefault("site", {})
    site["buildings"] = [
        {"id": "b1", "reference": True, "footprint": [[-0.1, -0.1], [10.1, -0.1], [10.1, 8.1], [-0.1, 8.1]],
         "rotation_deg": 0.0, "translate": [0.0, 0.0], "dz": 0.0, "orientation": "entrances", "evidence": ev},
        {"id": "b2", "reference": False, "footprint": [[19.9, -0.1], [30.1, -0.1], [30.1, 8.1], [19.9, 8.1]],
         "rotation_deg": 0.0, "translate": [20.0, 0.0], "dz": 1.0, "orientation": "entrances", "evidence": ev}]
    site["pools"] = [{"id": "pool_001", "polygon": [[1.0, -7.0], [9.0, -7.0], [9.0, -4.0], [1.0, -4.0]],
                      "depth": {"value": 1.5, "method": "assumed", "confidence": 0.0, "evidence": [], "note": "t"},
                      "source": "site_plan", "build": True, "evidence": ev}]
    return b


def test_the_ground_the_camera_model_and_the_site_view_know_the_second_block():
    from wenart.blender import build as BB
    from wenart.blender import exterior as E
    from wenart.blender import site as S

    prep = BB.prepare(_two_blocks(), "base", None)
    sp = prep["site"]
    assert len(sp["copy_holes"]) == 1 and [p["id"] for p in sp["pools"]] == ["pool_001"]
    parts = S.pool_parts(sp["pools"][0], sp["terrain"])
    assert parts["edge_z"] - parts["floor_z"] == pytest.approx(1.5)
    levels = prep["building"]["levels"]
    model = E.build_model(prep["building"], levels, prep["roof"], sp)
    assert model.inside((25.0, 4.0, 1.5)) == "copy" and model.inside((15.0, 4.0, 1.5)) is None
    plans, dropped = E.plan_exterior(model, prep["building"], levels, sp["plot"] or [], variant="base")
    site_views = [p for p in plans if p.get("site_view")]
    assert len(site_views) == 1 and site_views[0]["view"] == "aerial"
    for p in plans:
        assert model.inside(p["position"]) != "copy", p["name"]


DUMP = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    ob = bpy.data.objects.get("building_copy_b2")
    rows = {"copy": None if ob is None else {"type": ob.instance_type, "collection": ob.instance_collection.name,
            "children": sorted(c.name for c in ob.instance_collection.children),
            "t": [round(v, 4) for v in ob.matrix_world.translation]},
            "pools": sorted(o.name for o in bpy.data.objects if o.get("wenart_kind") == "site_pool")}
    json.dump(rows, open(out, "w"))
""")


def test_blender_places_the_second_block_as_an_instance(tmp_path):
    from wenart.blender import cli

    if cli.find_blender() is None:
        pytest.skip("no Blender binary (WENART_BLENDER)")
    path = tmp_path / "two.json"
    path.write_text(json.dumps(_two_blocks()), encoding="utf-8")
    manifest_path = cli.build(path, tmp_path / "scene", no_textures=True, preview_samples=1)
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    copies = (m.get("whole_building") or {}).get("copies")
    assert [c["id"] for c in copies] == ["b2"] and copies[0]["dz"] == 1.0
    assert any(o["kind"] == "building_copy" and o["wenart_id"] == "b2" for o in m["objects"])
    (tmp_path / "dump.py").write_text(DUMP, encoding="utf-8")
    dump = tmp_path / "dump.json"
    cli.run_blender(tmp_path / "dump.py", [str(dump)], blend=str(manifest_path.parent / "scene.blend"))
    rows = json.loads(dump.read_text(encoding="utf-8"))
    assert rows["copy"]["type"] == "COLLECTION" and rows["copy"]["t"] == [20.0, 0.0, 1.0]
    assert "level_L0" in rows["copy"]["children"]
    assert rows["pools"] == ["pool_001_basin", "pool_001_water"]


def test_an_agent_camera_inside_the_second_block_is_refused():
    from wenart.blender import exterior_checks as X

    b = _two_blocks()
    cam = {"action": "set", "view_id": "ext_9", "kind": "exterior", "position": [25.0, 4.0, 1.6],
           "target": [5.0, 4.0, 1.5], "reason": "t"}
    assert any("inside the building b2" in f for f in X.validate_camera_override(b, cam)["failed"])
    assert not any("b2" in f for f in X.validate_camera_override(b, dict(cam, position=[15.0, -12.0, 1.6]))["failed"])
