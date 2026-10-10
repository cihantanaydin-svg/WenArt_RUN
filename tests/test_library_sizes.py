"""Milestone 12 track B: the one real-size table (docs/milestone12.md §6.3 D23, contract §13.2 ``sizes``).

- every schema furniture type but ``unknown`` has width, depth, height (stair: none) and a default product that fits
  its own ranges; every library decor type too (by name and by ``decor_<name>``);
- the layout's sizes (``schemas.SIZE_OPTIONS``) fit in the front convention (the crib's long side is its front);
- ``fits`` checks the height of a box (the stub ignored it), ``product_size`` keeps the drawn orientation and snaps
  run types' depth only;
- the review against the ABO products whose titles give their size in cm: the 77 of the diagnosis are found, and
  every one whose title size matches its box and whose title names its type fits the table (the changed rows name
  their ABO source);
- the old readers of ``size_table.yaml`` (recognition, generic ingest, library) still read it.
"""
import math

import pytest
import yaml

from wenart.assets.audit import checks as CK
from wenart.assets.audit import items as I
from wenart.assets.audit import keywords as K
from wenart.furniture import catalog as C
from wenart.furniture import schemas
from wenart.furniture import sizes as S


def schema_types():
    from wenart import building as B
    return [t for t in B.load_schema()["$defs"]["furniture"]["properties"]["type"]["enum"] if t != "unknown"]


def test_every_type_has_width_depth_height_and_a_product_inside_its_ranges():
    for t in schema_types():
        r = S.real_range(t)
        assert r is not None, t
        assert set(r) == {"width", "depth", "height", "product"}
        (w0, w1), (d0, d1) = r["width"], r["depth"]
        assert 0 < w0 <= w1 and 0 < d0 <= d1, t
        if t == "stair":
            assert r["height"] is None and r["product"] is None
            continue
        h0, h1 = r["height"]
        assert 0 < h0 <= h1, t
        assert S.oriented_fits(t, r["product"], tolerance=0.0), (t, r["product"])
        for p in S.products(t):
            assert S.oriented_fits(t, p, tolerance=0.0), (t, p)
    assert S.real_range("unknown") is None
    assert S.real_range("no_such_type") is None
    assert not S.fits("unknown", (1.0, 1.0))


def test_decor_types_have_sizes_by_name_and_catalogue_type():
    for t in C.DECOR_TYPES:
        r = S.real_range(t)
        assert r is not None and r["height"] is not None and r["product"] is not None, t
        assert S.real_range(f"decor_{t}") == r
        assert S.fits(t, r["product"], 0.0), t
    assert set(S.decor_types()) == set(C.DECOR_TYPES)


def test_layout_sizes_fit_in_the_front_convention():
    """Width runs along the front: the crib's front is a long side (it was the short side before M12)."""
    for t, opts in schemas.SIZE_OPTIONS.items():
        for w, d in opts:
            assert S.oriented_fits(t, (w, d), tolerance=0.0), (t, w, d)
    assert S.real_range("crib")["width"] == (1.15, 1.50)


def test_fits_checks_the_height_of_a_box():
    assert S.fits("stove", (0.60, 0.60))
    assert S.fits("stove", (0.60, 0.60, 0.90))
    assert not S.fits("stove", (0.60, 0.60, 0.55))          # a generated stove built 0.55 m high (§1.6)
    assert S.fits("bed_double", (2.0, 1.6))                  # either orientation
    assert not S.fits("chair", (0.65 * 1.16, 0.5))
    assert S.fits("chair", (0.65 * 1.149, 0.5))


def test_product_size_keeps_the_drawn_orientation():
    assert S.product_size("toilet", (0.40, 0.70)) == (0.40, 0.70)
    assert S.product_size("toilet", (0.70, 0.40)) == (0.70, 0.40)
    w, d = S.product_size("toilet", (1.10, 0.62))           # a misread toilet: the nearest real one, same way round
    assert w > d and (round(d, 2), round(w, 2)) in {(0.38, 0.65), (0.40, 0.70), (0.45, 0.75), (0.36, 0.55)}
    assert S.product_size("bathtub", (0.72, 1.62)) == (0.70, 1.60)
    assert S.product_size("kitchen_counter", (3.30, 0.71)) == (3.30, 0.65)     # run: length kept, depth snapped
    assert S.product_size("kitchen_counter", (0.55, 2.10)) == (0.60, 2.10)
    assert S.product_size("unknown", (0.3, 0.4)) == (0.3, 0.4)


def test_scale_to_fit_and_range_error():
    assert S.scale_to_fit("bed_double", (1.6, 2.0, 1.0)) == 1.0
    assert math.isclose(S.scale_to_fit("bed_double", (0.8, 1.0, 0.5)), 1.85, rel_tol=0.02)
    assert S.scale_to_fit("bathtub", (1.32, 0.74, 0.80)) is None    # the generated tubs: no real proportions
    assert S.range_error("bed_double", (1.6, 2.0, 1.0)) == 0.0
    assert S.range_error("bunk_bed", (2.0, 1.0, 1.6)) > 0.5
    assert S.range_error("bunk_bed", (2.0, 1.0, 1.6), oriented=False) == 0.0


def titled_abo():
    out = []
    for it in I.load_items():
        if it["source"] != "abo":
            continue
        dims = CK.title_size(it["title"])
        if dims:
            out.append((it, dims))
    return out


def test_the_77_abo_titles_with_sizes_in_cm_fit_the_table():
    rows = titled_abo()
    assert len(rows) == 77                                    # the diagnosis (§1.6): 77 titles with sizes in cm
    misfits = []
    for it, dims in rows:
        if CK.title_size_error(dims, it["bbox_m"]) > 0.15:
            continue                                          # the listing's title belongs to another variant
        if K.title_check(it["title"], it["type"], "abo")["verdict"] != "match":
            continue                                          # filed under another type (the audit removes them)
        if CK.size_check(it, {"size": {"ok": 0.15, "fix": 0.30, "slack": 0.03}})["status"] != "ok":
            misfits.append((it["id"], it["type"], it["bbox_m"]))
    assert misfits == []


@pytest.mark.parametrize("abo_id,ftype", [("abo_B079X4CP3F", "dresser"), ("abo_B01557QQSW", "dresser"),
                                          ("abo_B07RMJPJMX", "tall_cabinet"), ("abo_B07374K536", "floor_lamp"),
                                          ("abo_B075YQ478W", "bar_stool")])
def test_the_changed_rows_hold_their_abo_source(abo_id, ftype):
    it = {i["id"]: i for i in I.load_items()}[abo_id]
    assert it["type"] == ftype
    assert S.fits(ftype, it["bbox_m"], 0.0), it["bbox_m"]
    row = yaml.safe_load(S._TABLE.read_text(encoding="utf-8"))["types"][ftype]
    assert abo_id[4:] in row["source"]


def test_the_old_readers_still_read_the_table():
    from wenart.assets import objaverse as OV
    from wenart.ingest.generic import symbols as GS
    from wenart.recognition import symbols as RS
    rs = RS.load_size_table()
    gs, src = GS.load_size_table()
    ov, tol = OV.load_size_table()
    assert set(rs) == set(gs) == set(ov) == set(schema_types())
    assert src.endswith("size_table.yaml") and tol == 0.15
    assert rs["crib"] == ((1.15, 1.50), (0.60, 0.85))
