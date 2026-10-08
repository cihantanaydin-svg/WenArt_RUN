"""The pipeline on a multi-region sheet (docs/milestone10.md §1.6a): one page record per region, the unit of the unit
check, every level in the registered frame with its heights from the section, alternatives as their own levels with
``same_as`` rooms, variants, slabs with stair voids, the roof, the site ground, the levels left out
(``failed_levels``), and a stale ``sheets.json`` analysed again."""
from __future__ import annotations

import json

import pytest

import wenart.sheets as SH
from _sheets_fixture import write_sheet
from wenart import building as B
from wenart.ingest import pipeline as P


def _build(tmp_path, name="p", brief=None, **opts):
    project = tmp_path / name
    project.mkdir()
    write_sheet(project / "sheet.dxf", **opts)
    if brief is not None:
        (project / "brief.yaml").write_text(brief, encoding="utf-8")
    building, build = P.run_project(project, tmp_path / f"{name}_out", no_ai=True)
    return building, build, tmp_path / f"{name}_out"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("pipe"))


def test_status_and_schema(built):
    building, build, out = built
    assert building["status"] == "ok", building["warnings"]
    assert B.validation_errors(building) == []
    assert (out / "sheets.json").is_file() and (out / "report.md").is_file()
    assert "## Building (sheets)" in (out / "report.md").read_text(encoding="utf-8")


def test_one_page_record_per_region(built):
    # §1.6b rows 2, 3: records for regions with use read / heights / exterior only (the title block stays in
    # sheets.json); the unit check overrode the header ($INSUNITS 4 = mm, the drawing is in cm): method unit_check.
    building, _, out = built
    pages = building["documents"][0]["pages"]
    assert [p["region_id"] for p in pages] == ["r2", "r3", "r4", "r5", "r6"]
    assert [p["class"] for p in pages] == ["floor_plan", "floor_plan", "floor_plan", "floor_plan", "section"]
    assert pages[2]["region_class"] == "alternative_floor_plan" and pages[2]["variant"] == "Açık mutfak"
    assert pages[4]["skip_reason"].startswith("section")
    for p in pages[:4]:
        scale = p["scale"]
        assert scale["metres_per_unit"] == 0.01 and scale["method"] == "unit_check"
        assert scale["evidence"]["rule"] == "unit_check" and scale["evidence"]["entity"] == "$INSUNITS=4"
        assert scale["evidence"]["text"].startswith("header mm; ") and "agree on cm" in scale["evidence"]["text"]
        assert p["debug_image"] == f"debug/sheet_dxf_p1_{p['region_id']}.png" and (out / p["debug_image"]).is_file()
        assert p["region_box"] and p["transform_to_building"]


def test_levels_with_heights_from_the_section(built):
    building, _, _ = built
    levels = {lv["id"]: lv for lv in building["levels"]}
    assert list(levels) == ["L-1", "L-1b", "L0", "L1"]
    assert {k: lv["kind"] for k, lv in levels.items()} == {"L-1": "basement", "L-1b": "basement", "L0": "floor",
                                                           "L1": "attic"}
    assert {k: lv["elevation"] for k, lv in levels.items()} == pytest.approx({"L-1": -3.0, "L-1b": -3.0, "L0": 0.0,
                                                                              "L1": 3.15}, abs=0.001)
    assert all(lv["elevation_source"] == "section" and lv["ceiling_height_source"] == "section"
               for lv in levels.values())
    assert levels["L0"]["ceiling_height"] == pytest.approx(3.0, abs=0.001)
    assert levels["L0"]["floor_to_floor"]["value"] == pytest.approx(3.15, abs=0.001)
    assert levels["L-1b"]["variant"] == "Açık mutfak" and levels["L-1b"]["base_level_id"] == "L-1"
    assert levels["L-1b"]["variant_group"] == "vg_L-1" and levels["L-1"]["variant"] == "base"
    assert {lv["region_id"] for lv in levels.values()} == {"r2", "r3", "r4", "r5"}
    walls = [w for w in building["walls"] if w["level_id"] == "L0"]
    assert all(w["height"] == pytest.approx(3.0, abs=0.001) for w in walls)


def test_every_level_in_one_frame(built):
    building, _, _ = built
    for level_id in ("L-1", "L-1b", "L0", "L1"):
        walls = [w for w in building["walls"] if w["level_id"] == level_id]
        xs = [p[0] for w in walls for p in (w["start"], w["end"])]
        ys = [p[1] for w in walls for p in (w["start"], w["end"])]
        # 20 cm outer walls around a 10 x 8 m outline whose outer corner is the frame's origin, on every level.
        assert (min(xs), min(ys), max(xs), max(ys)) == pytest.approx((0.0, 0.1, 10.0, 7.9), abs=0.02), level_id


def test_rooms_alternatives_and_variants(built):
    building, _, _ = built
    rooms = {r["id"]: r for r in building["rooms"]}
    assert rooms["r_L-1b_salon"]["same_as"] == "r_L-1_salon"
    assert rooms["r_L-1b_acik_mutfak"]["same_as"] is None
    assert rooms["r_L1_cocuk_odasi"]["room_subtype"] == "child"
    assert all("twin_of" in r for r in rooms.values())
    assert all(r["twin_transform"] is None and r["twin_residual_m"] is None for r in rooms.values())
    variants = {v["id"]: v for v in building["variants"]}
    assert variants["base"]["levels"] == ["L-1", "L0", "L1"]
    assert variants["base"]["rooms_changed"] == [] and variants["base"]["exterior_changed"] is False
    alt = variants["l-1b-acik-mutfak"]
    assert alt["levels"] == ["L-1b", "L0", "L1"] and alt["rooms_changed"] == ["r_L-1b_acik_mutfak"]
    assert alt["changes"] == [{"variant_group": "vg_L-1", "level_id": "L-1b", "replaces": "L-1"}]
    # The alternative's outer walls and openings match the base's: its exterior views are the base's.
    assert alt["exterior_changed"] is False and alt["evidence"][0]["region_id"] == "r4"
    levels = {lv["id"]: lv for lv in building["levels"]}
    assert levels["L-1"]["variant_slug"] == "base" and levels["L-1b"]["variant_slug"] == "acik-mutfak"


def test_evidence_names_the_region(built):
    building, _, _ = built
    region = {lv["id"]: lv["region_id"] for lv in building["levels"]}
    for key in ("walls", "rooms"):
        for x in building[key]:
            assert all(ev.get("region_id") == region[x["level_id"]] for ev in x["evidence"]
                       if ev.get("file") == "sheet.dxf"), x["id"]
    assert building["project"]["datum"]["value"] == 43.0


def test_slabs_roof_and_site(built):
    building, _, _ = built
    slabs = {s["id"]: s for s in building["slabs"]}
    # §1.6b row 8: the alternative's slabs equal the base's (same outline, its stair where the base's is): no
    # sl_L-1b and no sl_<above>__<variant>.
    assert set(slabs) == {"sl_L-1", "sl_L0", "sl_L1"}
    assert slabs["sl_L0"]["below_level_id"] == "L-1" and slabs["sl_L0"]["z_top"] == pytest.approx(0.0)
    assert all(s["thickness"] == pytest.approx(0.15) and s["thickness_source"] == "section" for s in slabs.values())
    assert [o["kind"] for o in slabs["sl_L0"]["openings"]] == ["stair_void"]
    stair = next(f for f in building["furniture"] if f["id"] == slabs["sl_L0"]["openings"][0]["furniture_id"])
    assert stair["type"] == "stair" and stair["level_id"] == "L-1"
    assert all(s["variants"] == [] for s in slabs.values())
    roof = building["roof"]
    assert roof["type"] == "gable" and roof["type_source"] == "section" and roof["planes"] == []
    assert roof["ridge_lines"] == [[[5.0, -0.5], [5.0, 8.5]]]
    assert roof["over_level_id"] == "L1" and roof["eaves_height"]["value"] == pytest.approx(3.65, abs=0.01)
    assert roof["profile"]["region_id"] == "r6" and roof["profile"]["cut_axis"] == "x"
    assert roof["profile"]["points"][0] == pytest.approx([-0.5, 3.65], abs=0.01) and roof["covering"] is None
    assert roof["covering_source"] is None and roof["knee_wall"]["value"] == pytest.approx(0.773, abs=0.01)
    assert building["facade"]["faces"] == [] and building["facade"]["elevations"] == []
    assert "default" not in building["facade"]
    site = building["site"]
    assert site["north_deg"] is None
    assert [g["side"] for g in site["ground"]["levels"]] == ["left", "right"] and site["ground"]["terrain"] == "flat"
    kinds = {c["kind"] for c in building["conflicts"]}
    assert {"unit_mismatch", "level_mark_mismatch"} <= kinds


def test_failed_level_is_left_out_with_the_levels_above(tmp_path):
    building, build, _ = _build(tmp_path, walls={"ground": False})
    left = {x["region_id"]: x["reason"] for x in building["levels_left_out"]}
    assert set(left) == {"r2", "r5"}
    assert "no building walls" in left["r2"] and "above the left-out level L0" in left["r5"]
    assert [lv["id"] for lv in building["levels"]] == ["L-1", "L-1b"]
    assert building["status"] == "ok"
    assert [v["levels"] for v in building["variants"]] == [["L-1"], ["L-1b"]]


def test_a_failed_alternative_drops_only_its_variant(tmp_path):
    building, build, _ = _build(tmp_path, walls={"alternative": False})
    assert [x["region_id"] for x in building["levels_left_out"]] == ["r4"]
    assert [lv["id"] for lv in building["levels"]] == ["L-1", "L0", "L1"]
    assert [v["id"] for v in building["variants"]] == ["base"] and building["status"] == "ok"


def test_only_alternative_levels_left_still_ok(tmp_path):
    # §1.6b row 7: the status stays ok while at least one level remains.
    building, build, _ = _build(tmp_path, walls={"ground": False, "basement": False})
    assert [lv["id"] for lv in building["levels"]] == ["L-1b"]
    assert building["status"] == "ok" and [v["id"] for v in building["variants"]] == ["l-1b-acik-mutfak"]
    assert any("only alternative levels remain" in w for w in building["warnings"])


def test_brief_variants_base_leaves_the_alternative_unbuilt(tmp_path):
    building, build, _ = _build(tmp_path, brief="variants: base\n")
    assert [lv["id"] for lv in building["levels"]] == ["L-1", "L0", "L1"]
    assert [v["id"] for v in building["variants"]] == ["base"]
    left = building["levels_left_out"]
    assert [x["region_id"] for x in left] == ["r4"] and "not built" in left[0]["reason"]
    assert building["status"] == "ok"


def test_site_plan_elevation_and_facade(tmp_path):
    # §1.6b row 12: drawn faces only (side, z range in building z, source elevation), one elevations entry with its
    # plan_check; the site plan's plot, parking, tree and labels; ground sides by compass once the north is known.
    building, build, _ = _build(tmp_path, exterior=True)
    assert building["status"] == "ok", build.review_reasons
    assert B.validation_errors(building) == []
    pages = {p["region_id"]: p for p in building["documents"][0]["pages"]}
    site_page = next(p for p in pages.values() if p["class"] == "site_plan")
    assert site_page["skip_reason"].startswith("site_plan") and site_page["transform_to_building"]
    faces = {f["material"]: f for f in building["facade"]["faces"]}
    assert faces["stone_cladding"]["side"] == "south" and faces["stone_cladding"]["z_range"] == pytest.approx([0, 1])
    assert faces["stone_cladding"]["level_id"] == "L0" and faces["stone_cladding"]["source"] == "elevation"
    assert faces["render"]["z_range"] is None and all(f["evidence"] for f in faces.values())
    (elev,) = building["facade"]["elevations"]
    assert (elev["side"], elev["windows"], elev["doors"], elev["title"]) == ("south", 3, 1, "GÜNEY GÖRÜNÜŞÜ")
    # The fixture's plans draw no window or door on the outer walls: the elevation's four are extra.
    assert elev["plan_check"]["matched"] == 0 and elev["plan_check"]["extra"] == 4
    assert elev["positions_m"][0]["sill"] == pytest.approx(1.0) and elev["positions_m"][0]["head"] == pytest.approx(2.5)
    site = building["site"]
    assert site["plot"]["source"] == "site_plan" and site["plot"]["polygon"][0] == pytest.approx([-7.0, -6.0])
    (parking,) = site["parking"]
    area = next(a for a in site["areas"] if a["id"] == parking["area_id"])
    assert area["kind"] == "parking" and area["build"] is False and area["label_raw"] == "OTOPARK"
    assert all(a["build"] is False for a in site["areas"])
    tree = next(d for d in site["decor"] if d["kind"] == "tree")
    assert tree["center"] == pytest.approx([-4.0, 11.0]) and tree["size"] == pytest.approx([2.0, 2.0])
    assert site["north_deg"]["value"] == pytest.approx(330.0, abs=3.0)
    # The section's left/right are -X/+X; with +Y ~30 deg west of north they face ~west and ~east.
    sides = [(g["side"], g["azimuth_deg"]) for g in site["ground"]["levels"]]
    assert [s for s, _ in sides] == ["west", "east"]
    assert sides[0][1] == pytest.approx(240.0, abs=3.0)


def test_failed_levels_stop(tmp_path):
    building, build, _ = _build(tmp_path, brief="failed_levels: stop\n", walls={"ground": False})
    assert building["status"] == "needs_review"
    assert any("r2 (L0)" in r for r in build.review_reasons)


def test_a_stale_sheets_json_is_analysed_again(tmp_path, built):
    project = tmp_path / "p"
    project.mkdir()
    write_sheet(project / "sheet.dxf")
    out = tmp_path / "out"
    SH.run(project, out, no_ai=True)
    doc = json.loads((out / "sheets.json").read_text(encoding="utf-8"))
    doc["inputs"][0]["sha256"] = "0" * 64
    doc["multi_region"] = False
    (out / "sheets.json").write_text(json.dumps(doc), encoding="utf-8")
    building, build = P.run_project(project, out, no_ai=True)
    assert any("ran again" in w for w in building["warnings"])
    assert len(building["levels"]) == 4


def test_a_crashing_analysis_falls_back_to_pages(tmp_path, monkeypatch):
    project = tmp_path / "p"
    project.mkdir()
    write_sheet(project / "sheet.dxf")

    def boom(*args, **kwargs):
        raise RuntimeError("broken")

    monkeypatch.setattr(SH, "run", boom)
    building, build = P.run_project(project, tmp_path / "out", no_ai=True)
    assert any(w.startswith("sheet analysis failed (RuntimeError: broken)") for w in building["warnings"])
    assert all("region_id" not in p for p in building["documents"][0]["pages"])


def test_debug_raster_of_a_region_renders_only_its_box(tmp_path):
    # §1.6b row 2: debug_image.raster_from_dxf(..., clip_box=) (plan crops of a region page).
    from wenart.ingest import debug_image as DI

    path = write_sheet(tmp_path / "sheet.dxf")
    box = (500.0, 2368.75, 1500.0, 3300.0)                # the ground-floor plan's region
    raster = DI.raster_from_dxf(path, width_px=400, clip_box=box)
    w, h = raster.image.size
    assert w == 400 and h == pytest.approx(400 * (box[3] - box[1]) / (box[2] - box[0]), abs=2)
    x0, y0 = raster.to_pixels((box[0], box[3]))
    x1, y1 = raster.to_pixels((box[2], box[1]))
    assert 0 < x0 < 20 and 0 < y0 < 20 and w - 20 < x1 < w and h - 20 < y1 < h
    assert raster.image.convert("L").getextrema()[0] < 128                # something is drawn


def test_the_building_origin_is_the_reference_walls_not_the_sheets_outline(tmp_path):
    # §1.6b row 1: the reference's outer wall faces (the core's step 8) fix the origin; the sheets outline starts at
    # an entrance step 0.3 m further out: every level, the roof outline and the profile move with the walls.
    building, build, _ = _build(tmp_path, step=True)
    assert build.frame_shift == pytest.approx((0.3, 0.0), abs=0.01)
    assert any(w.startswith("building frame:") for w in building["warnings"])
    for level_id in ("L-1", "L-1b", "L0", "L1"):
        walls = [w for w in building["walls"] if w["level_id"] == level_id]
        xs = [p[0] for w in walls for p in (w["start"], w["end"])]
        ys = [p[1] for w in walls for p in (w["start"], w["end"])]
        assert (min(xs), min(ys), max(xs), max(ys)) == pytest.approx((0.0, 0.1, 10.0, 7.9), abs=0.02), level_id
    xs = [p[0] for p in building["roof"]["outline"]]
    assert (min(xs), max(xs)) == pytest.approx((-0.5, 10.5), abs=0.02)
    assert building["roof"]["profile"]["points"][0][0] == pytest.approx(-0.5, abs=0.02)
    # The cut axis survives the step (review finding 4); the ridge sits over the walls' middle.
    assert building["roof"]["profile"]["cut_axis"] == "x"
    assert building["roof"]["ridge_lines"] == [[[5.0, -0.5], [5.0, 8.5]]]


def test_a_copy_of_a_level_is_cross_checked_not_an_alternative(tmp_path):
    # §1.6b row 4: the same level drawn twice with the same title is one level (the M7 master / secondary check).
    building, build, _ = _build(tmp_path, alternative_title="BODRUM KAT PLANI")
    assert [lv["id"] for lv in building["levels"]] == ["L-1", "L0", "L1"]
    assert [v["id"] for v in building["variants"]] == ["base"]
    pages = [p for p in building["documents"][0]["pages"] if p.get("level_id") == "L-1"]
    assert [p["region_id"] for p in pages] == ["r3", "r4"]
    assert building["status"] == "ok"


def test_an_alternative_whose_base_was_left_out_gets_its_slabs(tmp_path):
    # Review finding 5: the base basement fails, its alternative is built: the slab under the alternative and the
    # slab over it (with the alternative's stair void) are written for the variant, and listed.
    building, build, _ = _build(tmp_path, walls={"basement": False})
    assert [x["region_id"] for x in building["levels_left_out"]] == ["r3"]
    slabs = {s["id"]: s for s in building["slabs"]}
    under = slabs["sl_L-1__l-1b-acik-mutfak"]
    assert under["above_level_id"] == "L-1" and under["variants"] == ["l-1b-acik-mutfak"]
    over = slabs["sl_L0__l-1b-acik-mutfak"]
    assert over["below_level_id"] == "L-1" and [o["kind"] for o in over["openings"]] == ["stair_void"]
    stair = next(f for f in building["furniture"] if f["id"] == over["openings"][0]["furniture_id"])
    assert stair["level_id"] == "L-1b"
    assert any("base level L-1 left out" in w for w in building["warnings"])


def test_two_regions_of_one_level_on_one_sheet_keep_their_own_region_ids(tmp_path):
    # Review finding 14: the attic plan titled as the ground floor is a copy of L0 (r5) on the same sheet as its base
    # (r2): the base's walls, rooms and furniture name r2, the copy's cross-check evidence names r5.
    building, _, _ = _build(tmp_path, titles={"attic": "ZEMİN KAT PLANI"})
    level = next(lv for lv in building["levels"] if lv["id"] == "L0")
    assert sorted({e["region_id"] for e in level["evidence"]}) == ["r2", "r5"]
    for key in ("walls", "rooms", "furniture"):
        items = [x for x in building[key] if x["level_id"] == "L0"]
        assert items and all(x["evidence"][0]["region_id"] == "r2" for x in items), key
    walls = [w for w in building["walls"] if w["level_id"] == "L0"]
    assert all([e["region_id"] for e in w["evidence"]] == ["r2", "r5"] for w in walls)
    assert not any("left without a region_id" in w for w in building["warnings"])


def _two_plan_pdf(path) -> None:
    """One vector PDF page at 1:100: an L-shaped ground floor (x 0..10 m) and a basement of the same shape cut at
    x = 3 m, each wall drawn as its two face rings, each plan with its title, scale note and room names."""
    from reportlab.pdfgen import canvas as rl_canvas
    from shapely.geometry import Polygon

    pt = 72.0 / 25.4 * 10.0                      # page points per metre at 1:100
    c = rl_canvas.Canvas(str(path), pagesize=(1190.55, 841.89), invariant=1)
    c.setFont("Helvetica", 9)

    def plan(poly, ox, title, inner_x, labels):
        oy = 300.0
        outer = Polygon(poly)
        for ring in (outer.exterior.coords, outer.buffer(-0.2, join_style=2).exterior.coords):
            ring = list(ring)
            p = c.beginPath()
            p.moveTo(ox + ring[0][0] * pt, oy + ring[0][1] * pt)
            for x, y in ring[1:]:
                p.lineTo(ox + x * pt, oy + y * pt)
            p.close()
            c.drawPath(p, stroke=1, fill=0)
        c.rect(ox + inner_x * pt, oy + 0.2 * pt, 0.1 * pt, 5.6 * pt, stroke=1, fill=0)
        bx = min(x for x, _ in poly)
        c.drawString(ox + bx * pt, oy - pt, title)
        c.drawString(ox + (bx + 1) * pt, oy + pt, "OLCEK 1/100")
        for text, (x, y) in labels:
            c.drawString(ox + x * pt, oy + y * pt, text)

    plan([(0, 0), (10, 0), (10, 8), (4, 8), (4, 6), (0, 6)], 60.0, "ZEMIN KAT PLANI", 5.0,
         [("SALON", (1, 3)), ("MUTFAK", (7, 3))])
    plan([(3, 0), (10, 0), (10, 8), (4, 8), (4, 6), (3, 6)], 60.0 + 13 * pt, "BODRUM KAT PLANI", 6.0,
         [("DEPO", (3.5, 3)), ("KAZAN", (7.5, 3))])
    c.showPage()
    c.save()


def test_a_pdf_region_lands_in_its_registered_frame(tmp_path):
    # Review finding 13: a vector-PDF region uses the transform the sheets stage registered (moved by the reference's
    # frame shift) instead of the min corner of its own walls: the narrower basement is not pulled to x = 0.
    pytest.importorskip("reportlab")
    project = tmp_path / "pdf"
    project.mkdir()
    _two_plan_pdf(project / "plan.pdf")
    building, build = P.run_project(project, tmp_path / "out", no_ai=True)
    sheets = json.loads((tmp_path / "out" / "sheets.json").read_text(encoding="utf-8"))
    registered = {r["id"]: r["transform_to_building"] for r in sheets["regions"] if r["use"] == "read"}
    pages = {p["region_id"]: p["transform_to_building"] for p in building["documents"][0]["pages"]}
    assert build.reference_region == "r1" and max(abs(v) for v in build.frame_shift) < 0.005
    tf = pages["r2"]
    assert tf[2] == pytest.approx(registered["r2"][2] - build.frame_shift[0], abs=1e-6)
    assert tf[5] == pytest.approx(registered["r2"][5] - build.frame_shift[1], abs=1e-6)
    xs = [x for w in building["walls"] if w["level_id"] == "L-1" for x in (w["start"][0], w["end"][0])]
    assert min(xs) > 2.5                          # registered near x = 3 m, not at its own walls' corner
    assert not any("is not used" in w or "not a scale and shift" in w for w in building["warnings"])


def test_a_pdf_region_whose_registered_scale_is_not_the_cores_keeps_its_own_frame(tmp_path, monkeypatch):
    # Review finding 13: the origin of a registered transform holds only at its scale; when the core reads another
    # scale the region is read again in its own frame (origin at its walls) and the reason is listed.
    pytest.importorskip("reportlab")
    from wenart.ingest import classify as C

    real = C._region_record

    def scaled(rec, r, units, base_of):
        new = real(rec, r, units, base_of)
        if new.region_id == "r2" and new.region_transform:
            tf = list(new.region_transform)
            tf[0] *= 1.02
            tf[4] *= 1.02
            new.region_transform = tf
        return new

    monkeypatch.setattr(C, "_region_record", scaled)
    project = tmp_path / "pdf"
    project.mkdir()
    _two_plan_pdf(project / "plan.pdf")
    building, _ = P.run_project(project, tmp_path / "out", no_ai=True)
    xs = [x for w in building["walls"] if w["level_id"] == "L-1" for x in (w["start"][0], w["end"][0])]
    assert min(xs) == pytest.approx(0.0, abs=0.01)
    assert any("plan.pdf r2" in w and "differs from the registered scale" in w for w in building["warnings"])


@pytest.mark.parametrize("fmt, units, tf, origin, why", [
    ("pdf", None, [0.035278, 0.0, -14.98, 0.0, 0.035278, -10.58], (14.98, 10.58), None),
    ("dxf", 0.01, [0.01, 0.0, -2.0, 0.0, 0.01, -3.0], (2.0, 3.0), None),
    ("dxf", None, [0.01, 0.0, -2.0, 0.0, 0.01, -3.0], None, "no drawing unit for the region"),
    ("dxf", 0.001, [0.01, 0.0, -2.0, 0.0, 0.01, -3.0], None, "is not the drawing unit"),
    ("pdf", None, [0.0, -0.035, 1.0, 0.035, 0.0, 2.0], None, "a rotated or skewed registration"),
])
def test_the_region_origin_says_why_it_is_not_used(fmt, units, tf, origin, why):
    # Review finding 13: a PDF region's registered scale is its own unit; a transform that is not used names why.
    from wenart.ingest.classify import PageRecord

    record = PageRecord(file="a", page=1, format=fmt, kind="vector")
    record.region_id, record.region_transform, record.units_override = "r2", tf, units
    got, reason = P._region_origin(record)
    assert got == (pytest.approx(origin) if origin else None)
    assert (reason is None) if why is None else (why in reason)


def test_a_region_whose_outer_walls_do_not_close_is_left_out(tmp_path):
    # Review finding 10: the basement's east wall is not drawn; the west room closes and was taken for the building,
    # MUTFAK lay outside it and the level was built with one room (status ok). Now the region cannot be read: its
    # level is left out, named with the label.
    import ezdxf

    import _sheets_fixture as FX

    project = tmp_path / "open"
    project.mkdir()
    path = write_sheet(project / "sheet.dxf")
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    ox, oy = FX.PLANS["basement"][0]
    east = ox + FX.W - FX.OUTER
    for e in list(msp.query("LWPOLYLINE HATCH")):
        pts = list(e.get_points("xy")) if e.dxftype() == "LWPOLYLINE" else list(e.paths[0].vertices)
        if e.dxf.layer == "DUVAR" and abs(min(p[0] for p in pts) - east) < 1e-6 and min(p[1] for p in pts) > oy:
            msp.delete_entity(e)
    doc.saveas(path)
    building, _ = P.run_project(project, tmp_path / "out", no_ai=True)
    left = {x["region_id"]: x["reason"] for x in building["levels_left_out"]}
    assert list(left) == ["r3"] and "outer walls do not close" in left["r3"] and "'MUTFAK'" in left["r3"]
    assert [lv["id"] for lv in building["levels"]] == ["L-1b", "L0", "L1"]
    assert not any(r["level_id"] == "L-1" for r in building["rooms"])


def test_an_l_shaped_terrace_opening_reaches_over_its_parapets_to_the_roof_outline():
    # Lead item (track E, real02 ro_001): the L-shaped terrace along the west wall and round the north-west corner
    # grows over the west, south and north outer walls to the roof outline (§1.6b row 13), and to the centre line of
    # the inner wall at its east end; the walls along its inner edges are not crossed.
    from shapely.geometry import Point, Polygon

    from wenart.sheets import to_building as TB

    def wall(wid, a, b, exterior):
        return {"id": wid, "start": list(a), "end": list(b), "thickness": 0.2, "exterior": exterior}

    room = {"polygon": [[0.2, 0.2], [1.7, 0.2], [1.7, 10.3], [3.2, 10.3], [3.2, 11.8], [0.2, 11.8]]}
    walls = [wall("south", (0.0, 0.1), (15.2, 0.1), True), wall("north", (0.0, 11.9), (15.2, 11.9), True),
             wall("west", (0.1, 0.2), (0.1, 11.8), True), wall("inner_x", (1.8, 0.2), (1.8, 10.2), False),
             wall("inner_y", (1.7, 10.2), (8.0, 10.2), False), wall("east_end", (3.3, 10.3), (3.3, 11.8), False)]
    outline = [[-0.5, -0.5], [15.7, -0.5], [15.7, 12.5], [-0.5, 12.5]]
    polygon, parapets = TB.terrace_opening(room, walls, outline)
    assert sorted(parapets) == ["north", "south", "west"]
    assert polygon == [[-0.5, -0.5], [1.7, -0.5], [1.7, 10.3], [3.3, 10.3], [3.3, 12.5], [-0.5, 12.5]]
    grown = Polygon(polygon)
    # the parapet walls' stretches by the terrace lie under the opening; the inner wall along its east edge does not
    assert all(grown.contains(Point(p)) for p in [(0.1, 6.0), (1.0, 0.1), (2.5, 11.9)])
    assert not grown.contains(Point(1.8, 5.0))
