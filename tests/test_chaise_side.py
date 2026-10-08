"""CPU tests of the chaise side of a corner sofa (review finding 40 of Milestone 10, docs/milestone10.md §1.6b).

A placed L-shaped sofa has a ``shape.chaise_side`` (the viewer facing the sofa's front sees the chaise on that side).
A library corner sofa has a chaise on one side too, and a model with the chaise on the wrong side shows a mirrored L in
the render. Neither ABO names the side reliably (the "left-facing" of a listing depends on the maker) nor can a judge
tell left from right, so the thumbnail job measures the footprint (Blender, the model's own frame) and the catalogue
entry gets ``chaise_side`` from it and the model's front.

Covered: the footprint raster of an L (seeded, repeatable); the side for all four fronts and both sides (the models are
turned by rotations derived here, not by the code under test); a straight sofa, a U and a front that does not fit
(no side, with the reason); the thumbnail jobs (only corner sofas, a model measured before gets the footprint without a
new render); the catalogue entry; and, when Blender is installed (``WENART_BLENDER``), the whole way from a GLB through
the importer's frame.
"""
import json
from pathlib import Path

import pytest

from test_objaverse import Mirror, fake_runner, quiet
from test_recolour import box_glb
from wenart.assets import objaverse as OV

CFG = OV.load_config()
W, D, H, SEAT, CHAISE = 2.8, 1.6, 0.85, 0.95, 0.9      # a corner sofa: width, depth, height, seat depth, chaise width


def box_polys(x0, y0, z0, x1, y1, z1):
    """The six faces of a box as polygons (lists of world vertices)."""
    p = lambda x, y, z: (x, y, z)  # noqa: E731
    return [[p(x0, y0, z0), p(x1, y0, z0), p(x1, y1, z0), p(x0, y1, z0)], [p(x0, y0, z1), p(x1, y0, z1), p(x1, y1, z1), p(x0, y1, z1)],
            [p(x0, y0, z0), p(x1, y0, z0), p(x1, y0, z1), p(x0, y0, z1)], [p(x0, y1, z0), p(x1, y1, z0), p(x1, y1, z1), p(x0, y1, z1)],
            [p(x0, y0, z0), p(x0, y1, z0), p(x0, y1, z1), p(x0, y0, z1)], [p(x1, y0, z0), p(x1, y1, z0), p(x1, y1, z1), p(x1, y0, z1)]]


# Turning a sofa that faces -Y (its right is +X) so that it faces `front`; derived by hand: the front direction goes
# to the front axis, and the viewer's right (front x up) goes with it.
TURN = {"-Y": lambda x, y: (x, y), "+Y": lambda x, y: (-x, -y), "-X": lambda x, y: (y, -x), "+X": lambda x, y: (-y, x)}


def boxes_of(side="right", chaise_width=CHAISE, other_chaise=None):
    """Boxes (x0, y0, z0, x1, y1, z1) of a corner sofa facing -Y: the seat band along the back (y = +D/2), a chaise on
    the right (+X) or the left, and (a U-shape) a second one on the other side."""
    boxes = [(-W / 2, D / 2 - SEAT, 0.0, W / 2, D / 2, H)]
    if chaise_width:
        x0, x1 = (W / 2 - chaise_width, W / 2) if side == "right" else (-W / 2, -W / 2 + chaise_width)
        boxes.append((x0, -D / 2, 0.0, x1, D / 2 - SEAT, 0.45))
    if other_chaise:
        x0, x1 = (-W / 2, -W / 2 + other_chaise) if side == "right" else (W / 2 - other_chaise, W / 2)
        boxes.append((x0, -D / 2, 0.0, x1, D / 2 - SEAT, 0.45))
    return boxes


def sofa_polys(front="-Y", **kw):
    turn = TURN[front]
    out = []
    for x0, y0, z0, x1, y1, z1 in boxes_of(**kw):
        for poly in box_polys(x0, y0, z0, x1, y1, z1):
            out.append([(*turn(x, y), z) for x, y, z in poly])
    return out


def bounds_of(polys):
    pts = [v for poly in polys for v in poly]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def footprint_of(polys, **kw):
    mins, maxs = bounds_of(polys)
    return OV.footprint_occupancy(polys, mins, maxs, **kw)


# --------------------------------------------------------------------------
# The raster and the side
# --------------------------------------------------------------------------

def test_the_footprint_raster_of_an_l_is_seeded_and_shows_the_notch():
    polys = sofa_polys("-Y", side="right")
    fp = footprint_of(polys)
    assert fp == footprint_of(polys) and fp["grid"] == 24 and len(fp["rows"]) == 24 and all(len(r) == 24 for r in fp["rows"])
    assert set("".join(fp["rows"])) == {"0", "1"} and 0.6 < fp["filled"] < 0.9          # an L fills about 3/4 of its box
    rows = fp["rows"]
    assert rows[0][:8] == "0" * 8 and rows[0][-8:] == "1" * 8        # front row (y minimum): the chaise on +X only
    assert rows[-1] == "1" * 24                                      # back row: the seat band over the whole width
    assert footprint_of(polys, seed=1)["rows"] == rows               # another seed: the same cells (enough samples)
    assert footprint_of(polys, grid=12)["grid"] == 12


@pytest.mark.parametrize("front", ["-Y", "+Y", "-X", "+X"])
@pytest.mark.parametrize("side", ["right", "left"])
def test_the_chaise_side_follows_the_front_of_the_model(front, side):
    fp = footprint_of(sofa_polys(front, side=side))
    got, note = OV.chaise_side(fp, front, CFG)
    assert got == side, note
    assert "front strip left" in note
    flipped = OV.chaise_side(fp, {"-Y": "+Y", "+Y": "-Y", "-X": "+X", "+X": "-X"}[front], CFG)
    assert flipped[0] is None                      # the opposite front puts the chaise at the back: not an L any more


def test_a_narrow_or_wide_chaise_still_gives_its_side():
    for width in (0.6, 0.9, 1.1):
        for side in ("left", "right"):
            assert OV.chaise_side(footprint_of(sofa_polys("-Y", side=side, chaise_width=width)), "-Y", CFG)[0] == side


def test_no_side_for_a_straight_sofa_a_u_shape_an_unknown_front_or_no_measurement():
    straight = footprint_of(sofa_polys("-Y", chaise_width=0))
    side, note = OV.chaise_side(straight, "-Y", CFG)
    assert side is None and "both front halves filled" in note
    u_shape = footprint_of(sofa_polys("-Y", side="right", other_chaise=0.9))
    side, note = OV.chaise_side(u_shape, "-Y", CFG)
    assert side is None and "both front halves filled" in note
    # (An L turned by 90 degrees is an L again: the side is only as good as the front, which the documented front of
    # ABO or the agreement of both judges decide; a front on the wrong end gives a chaise at the back = no side.)
    assert OV.chaise_side(None, "-Y", CFG) == (None, "footprint not measured")
    assert OV.chaise_side({"grid": 24, "rows": []}, "-Y", CFG)[0] is None
    assert OV.chaise_side(straight, "up", CFG) == (None, "front axis 'up' unknown")
    assert OV.chaise_side(straight, None, CFG)[0] is None


def test_a_real_abo_corner_sofa_has_its_chaise_on_the_left_as_the_viewer_sees_it():
    """The footprint of ABO B0714QGLNB (a 2.45 x 2.43 x 0.87 m corner sofa, CC BY 4.0, Amazon.com), measured by the
    thumbnail job in Blender 5.2.2 on 8 Oct 2026: the seat band along +Y (the back, ABO's front is -Y) and the chaise
    on the low-x side, i.e. on the left of a viewer who faces the front."""
    rows = ["111111111000000000000000"] * 15 + ["1" * 24] * 9
    fp = {"grid": 24, "rows": rows, "filled": 0.6094, "samples": 60000}
    side, note = OV.chaise_side(fp, "-Y", CFG)
    assert side == "left" and "front strip left 0.75, right 0.00" in note
    assert OV.chaise_side(fp, "+X", CFG)[0] == "right"           # read with another front, the L is an L turned by 90 degrees
    assert OV.chaise_side(fp, "+Y", CFG)[0] is None              # the other front puts the chaise behind the band


def test_the_frames_and_thresholds_are_the_config_and_agree_with_the_building_schema():
    assert set(OV.FRONT_FRAMES) == {"-Y", "+Y", "-X", "+X"} and OV.FOOTPRINT_TYPES == ("sofa_corner",)
    assert set(CFG["footprint"]) >= {"grid", "samples", "min_fraction", "seed", "front_strip", "back_strip", "min_back",
                                     "min_chaise", "max_notch_ratio"}
    schema = json.loads((Path(OV.__file__).resolve().parents[1] / "schema" / "building.schema.json").read_text())
    shape = schema["$defs"]["furniture"]["properties"]["chaise_side"]["enum"]
    assert set(shape) == {"left", "right"}                          # the values this module writes


# --------------------------------------------------------------------------
# The thumbnail job and the catalogue entry
# --------------------------------------------------------------------------

def library_with_a_corner_sofa(tmp_path):
    m = Mirror(tmp_path / "mirror")
    uids = {"corner": m.add("sofa", likes=9, name="Big Sectional Couch"), "plain": m.add("sofa", likes=8, name="Oak Sofa")}
    out = tmp_path / "lib"
    OV.survey(m.write(), out, CFG, download=True, log=quiet)
    return out, uids


def l_shape(side="right"):
    polys = sofa_polys("-Y", side=side)
    pts = [v for poly in polys for v in poly]
    return pts


def runner_with_footprints(shapes, calls, seen):
    """The fake Blender of test_objaverse, plus what the real one adds for a job with ``footprint``."""
    base = fake_runner(shapes, calls, seen)

    def run(blender, jobs_path, log, timeout):
        rc = base(blender, jobs_path, log, timeout)
        jobs = json.loads(Path(jobs_path).read_text())
        for job in jobs["objects"]:
            if job.get("footprint"):
                rec = OV.read_json(Path(job["measure"]))
                polys = sofa_polys("-Y", side="right")
                rec["footprint"] = footprint_of(polys)
                OV.write_json(Path(job["measure"]), rec)
        return rc
    return run


def test_only_corner_sofas_are_measured_for_their_footprint_and_once(tmp_path):
    out, uids = library_with_a_corner_sofa(tmp_path)
    cands = {c["uid"]: c for c in OV.load_candidates(out)}
    assert OV.needs_footprint(cands[uids["corner"]]) and not OV.needs_footprint(cands[uids["plain"]])
    shapes = {uids["corner"]: (l_shape(), []), uids["plain"]: (l_shape(), [])}
    calls, seen = [], []
    doc, rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=runner_with_footprints(shapes, calls, seen), log=quiet)
    assert rc == 0
    assert {j["uid"]: j["footprint"] for j in seen} == {uids["corner"]: True, uids["plain"]: False}
    corner = doc["objects"][uids["corner"]]
    assert corner["status"] == "ready" and corner["type"] == "sofa_corner"
    assert corner["footprint"]["grid"] == 24 and OV.chaise_side(corner["footprint"], "-Y", CFG)[0] == "right"
    assert "footprint" not in doc["objects"][uids["plain"]]
    # a second run measures nothing; a model measured before the footprint existed is measured again without a render
    seen2: list = []
    OV.thumbnails(out, tmp_path / "work", CFG, runner=runner_with_footprints(shapes, [], seen2), log=quiet)
    assert seen2 == []
    measure = tmp_path / "work" / "measure" / f"{uids['corner']}.json"
    rec = OV.read_json(measure)
    rec.pop("footprint")
    OV.write_json(measure, rec)
    seen3: list = []
    doc3, _rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=runner_with_footprints(shapes, [], seen3), log=quiet)
    assert [(j["uid"], j["render"], j["footprint"]) for j in seen3] == [(uids["corner"], False, True)]
    assert doc3["objects"][uids["corner"]]["footprint"] == corner["footprint"]


def test_a_corner_sofa_goes_from_the_thumbnails_to_the_catalogue_with_its_chaise_side(tmp_path, monkeypatch):
    """Survey, thumbnails (fake Blender with the footprint), both judges, accept, write-catalog and the report: the
    entry of a corner sofa whose chaise is on the left holds ``chaise_side: left`` and its note, a plain sofa none."""
    from test_objaverse import answer, run_judges
    from types import SimpleNamespace
    from wenart.furniture import catalog as C
    out, uids = library_with_a_corner_sofa(tmp_path)
    left_points = [v for poly in sofa_polys("-Y", side="left") for v in poly]
    from test_objaverse import sofa_points
    plain_points = sofa_points()
    shapes = {uids["corner"]: (left_points, []), uids["plain"]: (plain_points, [])}
    base_run = fake_runner(shapes, [], [])

    def run(blender, jobs_path, log, timeout):
        rc = base_run(blender, jobs_path, log, timeout)
        for job in json.loads(Path(jobs_path).read_text())["objects"]:
            if job.get("footprint"):
                rec = OV.read_json(Path(job["measure"]))
                rec["footprint"] = footprint_of(sofa_polys("-Y", side="left"))
                OV.write_json(Path(job["measure"]), rec)
        return rc
    doc, rc = OV.thumbnails(out, tmp_path / "work", CFG, runner=run, log=quiet)
    assert rc == 0 and doc["objects"][uids["corner"]]["type"] == "sofa_corner", doc["objects"][uids["corner"]]
    assert doc["objects"][uids["plain"]]["type"] == "sofa" and doc["objects"][uids["corner"]]["geometric_front"] == "-Y"
    lib = SimpleNamespace(out=out, doc=doc)
    clients = {k: (lambda images, _p: answer(front=0)) for k in OV.MODEL_KEYS}
    assert run_judges(lib, clients=clients)["qwen"] == 0
    acc = OV.accept(out, CFG)
    assert {d["uid"] for d in acc["accepted"]} == set(uids.values()), acc["refused"]
    monkeypatch.setattr(C, "FURNITURE_TYPES", OV.furniture_types())
    base = json.loads(C.CATALOG_PATH.read_text(encoding="utf-8"))
    base["entries"] += [{"type": t, "parametric": True, "reason": "test"} for t in OV.furniture_types()
                        if t not in {e["type"] for e in base["entries"]} and t != "unknown"]
    base_path = tmp_path / "catalog.json"
    base_path.write_text(json.dumps(base), encoding="utf-8")
    cat = OV.write_catalog(out, tmp_path / "assets", CFG, base_catalog=base_path, log=quiet)
    by_type = {e["type"]: e for e in cat["entries"]}
    corner, plain = by_type["sofa_corner"], by_type["sofa"]
    assert corner["front_axis"] == "-Y" and corner["chaise_side"] == "left" and "front strip left" in corner["chaise_note"]
    assert "chaise_side" not in plain
    text = OV.report(out, CFG)
    assert "## Corner sofas (chaise side)" in text and f"`{corner['id']}`" in text and "| left |" in text


def entry_for(ftype, front, footprint):
    cand = {"uid": "abo_B0TEST", "source": "abo", "licence": "CC-BY-4.0", "licence_flag": None, "title": "Corner sofa",
            "glb_info": {"textured": True}, "units_known": True, "author": "Amazon.com", "source_url": "https://x.example/1"}
    obj = {"unit": {"scale": 1.0, "note": "n", "ok": True},
           "measure": {"bbox_min_raw": [-1.4, -0.8, 0.0], "bbox_max_raw": [1.4, 0.8, 0.85], "triangles": 1500, "vertices": 900}}
    if footprint is not None:
        obj["footprint"] = footprint
    dec = {"type": ftype, "kind": "furniture", "front_axis": front, "front_axis_confidence": "high", "front_axis_note": "n",
           "styles": ["modern"], "style_note": "s", "quality": [5, 4], "licence_flag": None, "has_mattress": None}
    return OV.catalog_entry(cand, obj, dec, "f" * 64, CFG)


def test_the_catalogue_entry_of_a_corner_sofa_records_the_side_and_the_reason_or_none():
    fp = footprint_of(sofa_polys("+X", side="left"))
    entry = entry_for("sofa_corner", "+X", fp)
    assert entry["chaise_side"] == "left" and "front strip" in entry["chaise_note"]
    assert entry_for("sofa_corner", "-Y", fp)["chaise_side"] is None                         # the front does not fit
    unmeasured = entry_for("sofa_corner", "-Y", None)
    assert unmeasured["chaise_side"] is None and unmeasured["chaise_note"] == "footprint not measured"
    plain = entry_for("sofa", "-Y", fp)
    assert "chaise_side" not in plain and "chaise_note" not in plain                         # only the corner sofa


# --------------------------------------------------------------------------
# The whole way through the importer's frame (needs Blender)
# --------------------------------------------------------------------------

def _blender():
    from wenart.blender.cli import find_blender
    return find_blender()


def gltf_boxes(front, side):
    """The sofa as boxes of a GLB (glTF Y up): the importer maps glTF (x, y, z) to the Z-up (x, -z, y), so a Z-up box
    (X0..X1, Y0..Y1, Z0..Z1) is the glTF box (X0, Z0, -Y1)..(X1, Z1, -Y0)."""
    turn = TURN[front]
    out = []
    for x0, y0, z0, x1, y1, z1 in boxes_of(side=side):
        (ax, ay), (bx, by) = turn(x0, y0), turn(x1, y1)
        lo, hi = (min(ax, bx), min(ay, by), z0), (max(ax, bx), max(ay, by), z1)
        out.append(((lo[0], lo[2], -hi[1]), (hi[0], hi[2], -lo[1]), 0))
    return out


@pytest.mark.skipif(_blender() is None, reason="no Blender binary (WENART_BLENDER)")
@pytest.mark.parametrize("front, side", [("-Y", "right"), ("-Y", "left"), ("+X", "right"), ("-X", "left")])
def test_real_blender_measures_the_footprint_and_the_side_of_a_glb(tmp_path, front, side):
    glb = box_glb(tmp_path / "sofa.glb", gltf_boxes(front, side), [{"pbrMetallicRoughness": {"baseColorFactor": [0.5] * 3 + [1]}}],
                  texture=False)
    work = tmp_path / "work"
    (work / "measure").mkdir(parents=True)
    measure = work / "measure" / "u.json"
    job = {"uid": "u", "glb": str(glb), "glb_sha256": "0" * 64, "measure": str(measure), "views": [], "deck": False,
           "footprint": True, "render": False}
    jobs = {"settings": OV._thumb_settings(CFG, "cpu"), "deadline": None, "work": str(work), "objects": [job]}
    jobs_path = OV.write_json(work / "blender_jobs.json", jobs)
    rc = OV.run_blender(_blender(), jobs_path, work / "blender.log", 600)
    assert rc == 0, (work / "blender.log").read_text()[-1500:]
    rec = OV.read_json(measure)
    assert rec["ok"], rec
    assert OV.chaise_side(rec["footprint"], front, CFG)[0] == side, rec["footprint"]["rows"]
