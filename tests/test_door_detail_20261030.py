"""UL179 (30 Oct 2026, real04 run 20261030-112241-full, cam_r_L1_koridor_1): "Door style is good but it is too plain,
make it better" (the glazed outside door d_L1_003: a flat frame and stiles round one pane, a flat casing, a lever on a
box). Every parametric door of a style family gets its family's joinery (``parametric.JOINERY``): glazing beads, a
profiled architrave (on plinth blocks in the period families), hinge tips, a lever on a rose or a backplate, a lock
cylinder and an outside door's weather bar. Pure tests; real04 is only the test case."""
from __future__ import annotations

import pytest

from wenart.blender import looks as LK
from wenart.blender import parametric as P

MODERN = {"family": "modern", "door": {"material": "wood_oak_light"}, "window_frame": {"material": "dark_bronze"}}
CLASSIC = {"family": "classic", "door": {"material": "wood_oak_light"}, "window_frame": {"material": "oak"}}
OUTSIDE = {"id": "d", "type": "door", "operation": "swing", "glazed": True,
           "outside_door": {"outside_room": "teras", "outward": [0.0, 1.0]}}
W, H, T = 0.824, 2.1, 0.12


def _door(style, opening=OUTSIDE, indoor=(-1.0,), **extra):
    look = dict(LK.door_look(style, opening), side=-1.0, architrave_faces=list(indoor), **extra)
    return P.door_parts(look, W, H, T)


def _roles(parts, role):
    return [p for p in parts if p["role"] == role]


def _span(parts, axis):
    vals = [v[axis] for p in parts for v in p["verts"]]
    return min(vals), max(vals)


def test_the_family_names_its_joinery():
    assert LK.door_product(MODERN)["joinery"] == "slim" and LK.door_product(CLASSIC)["joinery"] == "moulded"
    assert LK.door_product({"door": {"material": "wood_oak_light"}}) == {}           # no family: as before
    look = LK.door_look(MODERN, OUTSIDE)
    assert look["door_style"] == "glazed" and look["joinery"] == "slim" and look["outside"] is True
    assert "outside" not in LK.door_look(MODERN, {"id": "i", "type": "door", "joins": ["hall", "bedroom"]})


def test_the_glazed_outside_door_is_a_product():
    parts, rec = _door(MODERN)
    assert rec["joinery"] == "slim" and rec["weather_bar"] == 1.0 and rec["hinges"] == 3 and rec["lock_rose"]
    beads = _roles(parts, "bead")
    assert len(beads) == 8                                               # four round the pane on each face
    glass = _roles(parts, "glass")[0]
    gx0, gx1 = _span([glass], 0)
    assert _span(beads, 0)[0] >= gx0 - 1e-9 and _span(beads, 0)[1] <= gx1 + 1e-9
    ys = _span(beads, 1)
    assert ys[0] >= -P.DOOR_LEAF_T / 2.0 and ys[1] <= P.DOOR_LEAF_T / 2.0         # inside the leaf faces
    # the profiled architrave on the indoor face only: two jambs and the head, no longer plain boxes
    arch = _roles(parts, "architrave")
    assert len(arch) == 3 and all(len(p["verts"]) > 8 for p in arch) and _span(arch, 1)[1] < 0.0
    assert not _roles(parts, "plinth")                                   # the light families: no plinth blocks
    fillet = _roles(parts, "moulding")                                   # ... a stepped casing: the raised fillet
    assert len(fillet) == 3 and "moulding" in P.FIXED_ROLES
    assert _span(fillet, 1)[0] == pytest.approx(_span(arch, 1)[0] - P.FILLET["h"])          # it stands proud of the board
    assert _span(fillet + arch, 1)[0] == pytest.approx(-T / 2.0 - P.ARCHITRAVE_T_M)        # the casing's depth as before
    # the weather bar at the foot of the outside face
    bar = _roles(parts, "weather_bar")
    assert len(bar) == 1 and _span(bar, 1)[0] >= P.DOOR_LEAF_T / 2.0 - 1e-9 and _span(bar, 2)[1] < 0.05
    # hardware: a round rose, neck and bar on both faces, a lock cylinder in each lock rose, tipped hinges
    assert len(_roles(parts, "rose")) == 2 and len(_roles(parts, "lock_rose")) == 2
    assert len(_roles(parts, "lock_core")) == 2 and len(_roles(parts, "hinge_tip")) == 6
    assert {p["key"] for p in parts if p["role"] in ("rose", "lock_core", "hinge_tip", "weather_bar")} == {"handle"}


def test_every_part_is_closed_and_inside_the_opening():
    for style in (MODERN, CLASSIC):
        parts, _rec = _door(style, indoor=(-1.0, 1.0))
        for p in parts:
            assert P._signed_volume(p["verts"], p["faces"]) > 0.0, p["role"]
            assert all(len(set(f)) == len(f) >= 3 for f in p["faces"]), p["role"]
        x0, x1 = _span(parts, 0)
        reach = W / 2.0 - P.DOOR_FRAME_W + P.ARCHITRAVE_REVEAL_M + P.ARCHITRAVE_W_M + P.PLINTH_BLOCK["w_extra"]
        assert x0 >= -reach - 1e-6 and x1 <= reach + 1e-6
        assert _span(parts, 2)[0] >= -P.HINGE_TIP_H_M - 1e-9
        assert _span(parts, 2)[1] <= H - P.DOOR_FRAME_W + P.ARCHITRAVE_REVEAL_M + P.ARCHITRAVE_W_M + 1e-6


def test_the_period_families_mould_it():
    parts, rec = _door(CLASSIC, indoor=(-1.0, 1.0))
    assert rec["joinery"] == "moulded"
    assert len(_roles(parts, "plinth")) == 4                             # two per indoor face, at the jambs' feet
    assert all(_span([p], 2)[0] == 0.0 for p in _roles(parts, "plinth"))
    plates = _roles(parts, "rose")
    assert len(plates) == 2 and all(_span([p], 2)[1] - _span([p], 2)[0] == pytest.approx(P.BACKPLATE_M[1])
                                    for p in plates)
    assert min(len(p["verts"]) for p in _roles(parts, "bead")) >= 12          # ovolo beads: a curved section
    assert rec.get("weather_bar") is None                                # indoor on both faces: no outside face


def test_the_frame_census_and_the_open_pose_hold():
    parts, rec = _door(MODERN, indoor=(-1.0, 1.0))
    census = P.frame_census([p for p in parts if p["role"] in P.FRAME_CENSUS_ROLES], H)
    assert census["faces"] == {"-1": {"jambs": 2, "heads": 1}, "1": {"jambs": 2, "heads": 1}}
    look = dict(LK.door_look(CLASSIC, OUTSIDE), side=-1.0, architrave_faces=[-1.0])
    closed, _ = P.door_parts(look, W, H, T)
    opened, orec = P.door_parts(dict(look, leaf_state={"state": "open", "angle_deg": 90.0, "hinge": "start"}), W, H, T)
    assert orec.get("pose")
    fixed = sorted(tuple(v) for p in opened if p["role"] in P.FIXED_ROLES for v in p["verts"])
    assert fixed == sorted(tuple(v) for p in closed if p["role"] in P.FIXED_ROLES for v in p["verts"])
    assert _roles(closed, "plinth") and "plinth" in P.FIXED_ROLES
    moved = [p for p in opened if p["role"] in ("bead", "weather_bar")]
    still = [p for p in closed if p["role"] in ("bead", "weather_bar")]
    assert moved and sorted(tuple(v) for p in moved for v in p["verts"]) != \
        sorted(tuple(v) for p in still for v in p["verts"])                 # the beads and the bar go with the leaf


def test_a_library_doors_frame_takes_the_profile_and_no_family_keeps_its_door():
    plain = P.door_frame_parts(W, H, T, None, 1.0, (-1.0,), lining=False)
    shaped = P.door_frame_parts(W, H, T, None, 1.0, (-1.0,), lining=False, joinery="moulded")
    assert all(len(p["verts"]) == 8 for p in plain)
    assert len(_roles(shaped, "architrave")) == 3 and len(_roles(shaped, "plinth")) == 2
    old_look = dict(LK.door_look({"door": {"material": "wood_oak_light"}}, OUTSIDE), side=-1.0)
    parts, rec = P.door_parts(old_look, W, H, T)
    assert "joinery" not in rec and not _roles(parts, "bead") and not _roles(parts, "weather_bar")


class _Mat:
    """A stand-in for a model material (name only, no node tree)."""

    def __init__(self, name):
        self.name, self.use_nodes, self.node_tree = name, False, None


def test_ul191_an_inside_doors_narrow_lites_are_satin_glass_never_slots():
    """UL191 (user: "Something wrong with this door in the kitchen"; real04 run 20261030-112241-full, cam_r_L-1_mutfak_2:
    the inside door HSSD 204-7, open flat against a slatted wall, showed the wall through two narrow clear lites)."""
    from wenart.blender import materials as M
    from wenart.blender import opening_build as OB

    leaf, lite = _Mat("material_1"), _Mat("Glass")
    assert OB.satin_lites([leaf, lite], [0.985, 0.015], inside=True)                 # narrow lites: satin
    assert not OB.satin_lites([leaf, lite], [0.6, 0.4], inside=True)                 # a glazed leaf keeps clear glass
    assert not OB.satin_lites([leaf, lite], [0.985, 0.015], inside=False)            # an outside door's lites: clear
    assert not OB.satin_lites([leaf], [1.0], inside=True)                            # no glass: nothing to do
    assert OB.glass_share([leaf, lite, _Mat("Window_Pane")], [0.9, 0.06, 0.04]) == pytest.approx(0.10)
    assert 0.0 < M.SATIN_GLASS["transmission"] < 1.0 and M.SATIN_GLASS["roughness"] >= 0.3      # milky, diffused
    import inspect

    src = inspect.getsource(OB.build_library_opening)
    assert "satin_lites(" in src and "satin_glass()" in src and '"satin_glass": satin' in src


def test_ul191_a_panel_material_is_never_glass():
    from wenart.blender import opening_build as OB
    from wenart.blender import opening_models as OM

    for name in ("Door_Panel", "panel_inlay", "PANELS", "FP_DOORFRAME", "material_1"):
        assert not OB.glass_named(name) and not OB.is_glass(_Mat(name)) and not OM._glass_named(name), name
    for name in ("Glass", "window_pane", "Pane", "panes_01", "cam_1", "glazing"):
        assert OB.glass_named(name) and OM._glass_named(name), name


def test_the_detail_stays_light():
    for style in (MODERN, CLASSIC):
        parts, _rec = _door(style, indoor=(-1.0, 1.0))
        assert sum(len(p["verts"]) for p in parts) <= 1400            # many doors per house: the build time
