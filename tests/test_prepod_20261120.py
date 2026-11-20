"""The fixes of the final pre-pod check (20 Nov 2026, SENSE sections): CPU only, synthetic fixtures."""
from types import SimpleNamespace

from shapely.geometry import box

from wenart.ingest import completion as CP
from wenart.sheets import roof_frame as RF


# --------------------------------------------------------------------------- R20-01 / BP-03: a sheet frame is no roof
def _txt(text, x, y):
    return SimpleNamespace(text=text, point=(x, y))


def test_a_double_sheet_frame_with_street_texts_is_no_roof():
    walls = box(0, 0, 16.05, 11.12)                           # metres = units (mpu 1)
    frame = box(-1.15, -1.32, 17.79, 13.27)
    top = SimpleNamespace(texts=[_txt("AHMET KAYA CADDESİ", 16.9, 5.0), _txt("3406 PARSEL", 8.0, 12.5)])
    why = RF.reject(top, 1.0, SimpleNamespace(id="LWPOLYLINE:9AD"), frame, [], walls=walls)
    assert why and "9AD" in why
    near = box(-0.6, -0.6, 16.65, 11.72)                      # 0.6 m all round: the edges alone pass ...
    assert RF.reject(SimpleNamespace(texts=[]), 1.0, SimpleNamespace(id="x"), near, [], walls=walls) is None
    top2 = SimpleNamespace(texts=[_txt("AHMET KAYA CADDESİ", 16.4, 5.0)])     # ... a street name in the ring does not
    assert "texts" in RF.reject(top2, 1.0, SimpleNamespace(id="x"), near, [], walls=walls)


def test_a_real_eaves_loop_and_a_break_line_on_the_walls_stay():
    walls = box(0, 0, 12, 9)
    eaves = box(-0.7, -0.7, 12.7, 9.7)
    top = SimpleNamespace(texts=[_txt("SAÇAK", 6.0, 9.4), _txt("+12.00", 12.4, 4.0), _txt("P150/120", 12.3, 2.0)])
    assert RF.reject(top, 1.0, SimpleNamespace(id="e"), eaves, [], walls=walls) is None
    assert RF.break_inside(top, 1.0, SimpleNamespace(id="e"), SimpleNamespace(id="b"), box(0.1, 0.1, 11.9, 8.9),
                           walls=walls)
    assert not RF.break_inside(top, 1.0, SimpleNamespace(id="e"), SimpleNamespace(id="b"),
                               box(-0.5, -0.5, 12.5, 9.5), walls=walls)      # a 'break' outside the walls


def test_a_plan_lines_roof_with_no_height_over_a_counted_storey_sits_on_its_ceiling():
    b = {"levels": [{"id": f"L{k}", "order": k, "elevation": 3.0 * k, "ceiling_height": 2.7} for k in range(5)],
         "roof": {"type": "mansard", "type_source": "plan_roof_lines", "eaves_height": None, "over_level_id": "L0"},
         "warnings": []}
    build = SimpleNamespace(building=b, warn=b["warnings"].append)
    why = CP._plan_roof_eaves(build, b, {"L2", "L3", "L4"})
    assert why and b["roof"]["eaves_height"]["value"] == 14.7 and b["roof"]["eaves_height"]["method"] == "assumed"
    assert b["roof"]["over_level_id"] == "L4"
    b["roof"]["type_source"] = "section"
    b["roof"]["eaves_height"] = None
    assert CP._plan_roof_eaves(build, b, {"L2", "L3", "L4"}) is None          # a section roof: the rebase's job
