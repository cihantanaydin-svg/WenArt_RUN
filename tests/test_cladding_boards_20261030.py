"""UL204 (30 Oct 2026, real04 run 20261030-112241-full): "the wood cladding by the door also looks streaky, fix it too":
the plank-siding photo read as smeared streaks. A wood cladding is laid as boards (``parquet`` pattern ``boards``):
straight boards in rows, the ends staggered per row, each board its own cut of the walnut veneer, its own tone and
grooved joints; upright on a wall. Pure tests."""
from wenart.blender import materials as M
from wenart.blender import parquet as PQ
from wenart.style import vocabulary as V


def test_boards_tile_the_wall_with_staggered_ends():
    p = PQ.CLADDING_BOARDS["wood_cladding"]
    assert p["pattern"] == "boards" and p["turn_deg"] == 90.0 and 0.08 <= p["width_m"] <= 0.2
    flat = dict(p, turn_deg=0.0)
    ends = set()
    for row in range(6):
        y = (row + 0.5) * flat["width_m"]
        c = PQ.cell("boards", 0.0, y, flat)
        assert 0.0 <= c["along_m"] < flat["length_m"] and abs(c["across_m"] - flat["width_m"] / 2.0) < 1e-9
        if min(c["along_m"], flat["length_m"] - c["along_m"]) > PQ.SEAM_M:
            assert c["seam"] == 0.0                                  # mid-row, away from the board's ends
        ends.add(round(flat["length_m"] - c["along_m"], 3))
    assert len(ends) == 6                                            # every row's ends sit elsewhere
    assert PQ.cell("boards", 0.0, flat["width_m"] * 1.0001, flat)["seam"] > 0.9    # on the row joint
    up = PQ.cell("boards", 0.0, 0.3, p)                              # turned 90: the boards stand upright
    across = PQ.cell("boards", 0.06, 0.3, p)
    assert up["plank"] != across["plank"] or abs(up["across_m"] - across["across_m"]) > 0.05


def test_the_cladding_takes_the_boards_and_a_walnut_veneer():
    assert M.parquet_of({"parquet": PQ.CLADDING_BOARDS["wood_cladding"]})["pattern"] == "boards"
    assert V.veneer_for("wood_cladding") == "wood_veneer_walnut"
    assert M.parquet_veneer_asset("wood_cladding") == V.FURNITURE_MATERIALS["wood_veneer_walnut"]["asset"]
    ins = PQ.group_inputs(PQ.CLADDING_BOARDS["wood_cladding"], 1.0)
    assert ins["Length"] == 3.0 and abs(ins["Cos"]) < 1e-9 and abs(ins["Sin"] - 1.0) < 1e-9
