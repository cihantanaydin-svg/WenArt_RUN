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


# --------------------------------------------------------------------------- BP-01: light wells, party walls
def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _wall(wid, a, b, t=0.2, **kw):
    return dict({"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t}, **kw)


def _light_well_plan():
    """A 0.15 m party wall on the west (x 0); a light well (shaft, subtype light_well) against it between a WC (north)
    and a bedroom (south, east of it); the WC's window onto the light well; the bedroom's dark inside window."""
    party = {"text": "bitişik", "reason": "a blank party wall: no window, no balcony"}
    walls = [_wall("w_party", (0, 0), (0, 9), t=0.15, exterior=True, party_wall=party),
             _wall("w_s", (0, 0), (8, 0), exterior=True), _wall("w_e", (8, 0), (8, 9), exterior=True),
             _wall("w_n", (8, 9), (0, 9), exterior=True), _wall("w_lw_n", (0, 5), (2, 5)), _wall("w_lw_s", (0, 3), (2, 3)),
             _wall("w_lw_e", (2, 3), (2, 5)), _wall("w_mid", (2, 0), (2, 3))]
    rooms = [{"id": "r_lw", "level_id": "L0", "label": "Işıklık", "room_type": "shaft", "room_subtype": "light_well",
              "polygon": _rect(0.1, 3.1, 1.9, 4.9)},
             {"id": "r_wc", "level_id": "L0", "label": "WC", "room_type": "wc", "polygon": _rect(0.1, 5.1, 7.9, 8.9)},
             {"id": "r_bed", "level_id": "L0", "label": "Oda", "room_type": "bedroom", "polygon": _rect(2.1, 0.1, 7.9, 4.9)},
             {"id": "r_hall", "level_id": "L0", "label": "Hol", "room_type": "hall", "polygon": _rect(0.1, 0.1, 1.9, 2.9)}]
    ops = [{"id": "win_wc", "type": "window", "level_id": "L0", "wall_id": "w_lw_n", "center": [1.0, 5.0],
            "width": 0.6, "height": 0.6, "sill_height": 1.5},
           {"id": "win_in", "type": "window", "level_id": "L0", "wall_id": "w_mid", "center": [2.0, 1.5],
            "width": 1.0, "height": 1.2, "sill_height": 0.9}]
    return {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls,
            "rooms": rooms, "openings": ops, "furniture": []}


def test_a_light_well_is_open_air_and_a_party_wall_takes_no_opening():
    from wenart.blender import architect_actions as AA

    b = _light_well_plan()
    plan = AA.Plan(b)
    assert AA.Plan.is_outside(plan.room["r_lw"]) and AA.is_open_air(plan.room["r_lw"])
    assert plan.outer_runs(plan.walls["w_party"], "r_wc") == []                  # the party wall has no outer run
    assert plan.outer_runs(plan.walls["w_lw_n"], "r_wc")                          # the light well's wall has one
    ok, why = AA.act_move_window(plan, "W2", {}, "win_wc")
    assert ok and "already looks outside" in why and b["openings"][0]["wall_id"] == "w_lw_n"
    AA.act_move_window(plan, "W2", {}, "win_in", "r_bed")
    assert next(o for o in b["openings"] if o["id"] == "win_in")["wall_id"] != "w_party"
