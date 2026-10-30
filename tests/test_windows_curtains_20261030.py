"""UL181 (30 Oct 2026, real04 run 20261030-112241-full, the top-floor play room: "This window and curtain arrangement
needs a rework": the architect widened the window to 4 m after the decor stage, the 2.4 m curtain hung mid-glass, the
glazing read frameless) and UL197 ("Give more detail to window frames": four flat bars round one pane). Pure tests; real04
is only the test case."""
from pathlib import Path

import pytest

from wenart.blender import parametric as P
from wenart.blender import window_decor as WD
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA

ROOT = Path(__file__).resolve().parents[1]


def _volume(part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


# ------------------------------------------------------------------------------------------- UL197: the window product

def test_a_wide_glazing_is_divided_into_real_products():
    low = P.window_division(4.0, 0.2)
    assert (low["kind"], low["panes"], low["opening"]) == ("slider", 2, [1]) and "lift-and-slide" in low["why"]
    high = P.window_division(4.0, 0.9)
    assert (high["kind"], high["panes"], high["opening"]) == ("casement", 4, [0, 3])
    assert P.window_division(2.0, 0.9)["panes"] == 2 and P.window_division(1.0, 0.9)["opening"] == [0]
    drawn = P.window_division(4.0, 0.2, mullions=2)
    assert drawn["panes"] == 3 and drawn["drawn"]


@pytest.mark.parametrize("material,width,sill", [("dark_bronze", 4.0, 0.2), ("pvc_white", 1.2, 0.9),
                                                 ("steel_black", 3.0, 0.9), ("oak", 2.0, 0.9)])
def test_the_window_product_has_frame_step_sashes_gaskets_handles(material, width, sill):
    h, t = 1.5, 0.25
    parts, rec = P.window_product_parts({"material": material}, width, h, t, inside=-1, sill=sill)
    fw, depth = P.window_profile(material)
    assert rec["frame_width"] == fw and rec["frame_depth"] == pytest.approx(depth)
    assert all(_volume(p) > 0 for p in parts)                                         # closed, wound outwards
    roles = [p["role"] for p in parts]
    n, opening = rec["product"]["panes"], rec["product"]["opening"]
    assert roles.count("glass") == n and roles.count("mullion") == n - 1 and rec["mullions"] == n - 1
    assert roles.count("gasket") == 4 * n and roles.count("frame") == 8                # the frame and its step ring
    assert roles.count("sash") == 4 * len(opening) and roles.count("bead") == 4 * (n - len(opening))
    assert roles.count("handle") >= len(opening)
    assert ("track" in roles) == (rec["product"]["kind"] == "slider")
    for p in parts:
        xs, ys, zs = [v[0] for v in p["verts"]], [v[1] for v in p["verts"]], [v[2] for v in p["verts"]]
        if p["role"] == "sill":
            continue
        assert min(xs) >= -width / 2.0 - 1e-6 and max(xs) <= width / 2.0 + 1e-6, p["role"]
        assert min(zs) >= -1e-6 and max(zs) <= h + 1e-6, p["role"]
        if p["role"] != "handle":
            assert min(ys) >= -depth / 2.0 - 1e-6 and max(ys) <= depth / 2.0 + 1e-6, p["role"]
        else:
            assert max(ys) < 0.0                                                       # on the room side (-y)
    keys = {p["key"] for p in parts}
    assert keys <= {"frame", "gasket", "glass", "handle", "sill"}


def test_the_shell_builds_the_window_product_with_a_dark_gasket_and_its_handles():
    src = (ROOT / "wenart" / "blender" / "shell.py").read_text()
    assert "P.window_product_parts(" in src and '"window_handles"' in src
    from wenart.blender import shell
    assert {"sash", "bead", "gasket", "track"} <= set(shell.WINDOW_FRAME_ROLES)
    from wenart.style.profile import _entry
    assert (_entry(shell.WINDOW_GASKET_MATERIAL) or {}).get("kind") == "metal"        # a dark slug the library has


# ------------------------------------------------------------------------------------- UL181: curtains follow windows

def _building(win_width=4.0, curtain_width=2.4, sill=0.2, head=1.714, door=None, curtain_top=1.69):
    wall = {"id": "w1", "level_id": "L1", "start": [0.0, 0.0], "end": [0.0, 10.0], "thickness": 0.2}
    openings = [{"id": "win1", "type": "window", "level_id": "L1", "wall_id": "w1", "center": [0.0, 4.5],
                 "width": win_width, "sill_height": sill, "height": head - sill}]
    if door is not None:
        openings.append({"id": "d1", "type": "door", "level_id": "L1", "wall_id": "w1", "center": [0.0, door],
                         "width": 0.9, "height": 2.1})
    curtain = {"id": "c1", "type": "curtain", "level_id": "L1", "room_id": "r1", "window_id": "win1",
               "center": [0.2, 4.5, 0.01], "size": [curtain_width, 0.14, curtain_top - 0.01], "rotation_deg": 90.0,
               "wall_point": [0.1, 4.5], "colour": "cream", "layers": ["sheer", "drape"]}
    return {"levels": [{"id": "L1", "elevation": 3.15, "ceiling_height": 2.6}], "walls": [wall],
            "openings": openings, "decor": [curtain]}


def test_a_curtain_of_a_widened_window_spans_the_whole_glazing_again():
    b = _building()
    rec = WD.refit(b)
    c = b["decor"][0]
    assert [r["id"] for r in rec] == ["c1"] and c["refit"]["lesson"] == "UL181"
    assert c["size"][0] == pytest.approx(4.0 + 2 * WD.CURTAIN_OVERLAP_M)
    assert c["center"][:2] == [0.2, 4.5] and c["size"][1] == 0.14 and c["layers"] == ["sheer", "drape"]
    assert c["center"][2] + c["size"][2] >= 1.714                                     # the rod over the new head
    assert c["refit"]["was"]["size"][0] == 2.4
    again = WD.refit(b)
    assert again == []                                                                # it spans now: left alone


def test_a_curtain_that_spans_its_window_is_left_alone_and_a_door_narrows_one_side():
    ok = _building(win_width=2.0, curtain_width=2.4, head=1.6)
    assert WD.refit(ok) == [] and "refit" not in ok["decor"][0]
    near = _building(door=7.2)                       # the door with its margin from 6.65: the rod's right end 0.15 m
    WD.refit(near)
    c = near["decor"][0]
    s0, s1 = c["center"][1] - c["size"][0] / 2.0, c["center"][1] + c["size"][0] / 2.0
    assert s1 <= 7.2 - 0.45 - WD.OPENING_MARGIN_M + 1e-6 and s1 >= 6.5 + WD.CURTAIN_MIN_OVERLAP_M - 1e-6
    assert s0 == pytest.approx(2.5 - WD.CURTAIN_OVERLAP_M)
    blocked = _building(door=6.9)                    # from 6.35: no room past the glazing's right side
    WD.refit(blocked)
    assert blocked["decor"][0]["build"] is False and "UL181" in blocked["decor"][0]["not_built_reason"]


def test_the_build_refits_after_the_answers_and_the_constants_match_the_decor_stage():
    src = (ROOT / "wenart" / "blender" / "build.py").read_text()
    assert "WD.refit(vb)" in src and src.index("WD.refit(vb)") > src.index("AA.apply_answers(")
    assert WD.CURTAIN_OVERLAP_M == DA.CURTAIN_OVERLAP_M and WD.CURTAIN_MIN_OVERLAP_M == DA.CURTAIN_MIN_OVERLAP_M
    assert WD.CURTAIN_ROD_ABOVE_M == DA.CURTAIN_ROD_ABOVE_M and WD.BLIND_WIDTH_EXTRA_M == DA.BLIND_WIDTH_EXTRA_M
    assert WD.BLIND_ROLLER_ABOVE_M == DA.BLIND_ROLLER_ABOVE_M and WD.CEILING_CLEAR_M == DA.CEILING_CLEAR_M
    assert WD.SLOPE_CLEAR_M == D.WINDOW_DECOR_CEILING_CLEAR_M and WD.OPENING_MARGIN_M == D.OPENING_MARGIN_M
    assert WD.WALL_END_MARGIN_M == D.WALL_END_MARGIN_M
