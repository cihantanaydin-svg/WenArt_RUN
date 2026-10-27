"""27 Oct 2026 (user on real06: "this in front of a window not making sense": a drawn dresser under a 0.90 m sill got a
1.44 m tall chest that covered the window): a piece whose back stands on a window's wall gets no model taller than
the sill (``fit.window_cap`` inside ``fit.piece_ceiling``), and the model review's M2 reports one that does."""
from __future__ import annotations

from wenart.blender import model_review as MR
from wenart.furniture import fit as F

from test_decor_m8 import RID, room_building


def _room():
    return room_building(5.0, 4.0, "bedroom",
                         furniture=[("dresser", (2.5, 0.28), 0.0, (1.2, 0.55)),       # back on the south wall
                                    ("chair", (2.5, 0.9), 0.0, (0.45, 0.45)),
                                    ("wardrobe", (1.0, 0.31), 0.0, (1.0, 0.6)),
                                    ("dresser", (2.5, 3.7), 180.0, (1.2, 0.55))],      # the north wall: no window
                         windows=(("win1", "s", 2.0, 2.4),))


def test_a_piece_against_a_window_wall_takes_a_model_under_the_sill():
    b = _room()
    dresser, chair, wardrobe, north = b["furniture"]
    assert F.window_cap(b, dresser) == 0.9 - F.WINDOW_SILL_GAP_M
    assert F.window_cap(b, chair) is None                      # not a type whose back stands on the wall
    assert F.window_cap(b, wardrobe) is None                   # no real wardrobe that low: the placement moves it
    assert F.window_cap(b, north) is None                      # no window on its wall
    ceiling = F.piece_ceiling(b, dresser)
    assert not F.under_ceiling(1.44, ceiling) and F.under_ceiling(0.85, ceiling)
    assert F.piece_ceiling(b, north) is None


def test_m2_reports_a_piece_that_covers_a_window():
    b = _room()
    dresser = b["furniture"][0]
    manifest = {"objects": [{"kind": "furniture", "element_id": dresser["id"], "type": "dresser", "room_id": RID,
                             "box3d": {"center": [2.5, 0.28, 0.72], "size": [1.2, 0.55, 1.44]}}]}
    got, n = MR.over_sills(manifest, b, {RID: 0.0})
    assert n == 1 and len(got) == 1 and got[0]["metrics"]["rule"] == "window" and "covers the window" in got[0]["message"]
    manifest["objects"][0]["box3d"] = {"center": [2.5, 0.28, 0.42], "size": [1.2, 0.55, 0.84]}
    assert MR.over_sills(manifest, b, {RID: 0.0})[0] == []
