"""30 Oct 2026, the user's review of real04 run 20261030-112241-full: "Better toilet paper roll model is needed" (UL183),
"More detailed models would be nice here" / "Better models with more details is needed" (UL184, the vanity), "Better
quality models with more details needed for the little items fruit ball etc" (UL186, the kitchen worktop). The small
objects are real products (``wenart.blender.small_parts``). Pure tests; real04 is only the test case."""
from __future__ import annotations

from wenart.blender import bath_objects as BO
from wenart.blender import bath_parts as BT
from wenart.blender import kitchen_details as KD
from wenart.blender import parametric as P
from wenart.blender import small_parts as SM


def _closed(part) -> bool:
    """Every edge of the part is shared by exactly two faces, in opposite directions."""
    edges = {}
    for f in part["faces"]:
        for i in range(len(f)):
            e = (f[i], f[(i + 1) % len(f)])
            edges[e] = edges.get(e, 0) + 1
    return all(n == 1 and edges.get((b, a)) == 1 for (a, b), n in edges.items())


def _check(parts, box, slack=1e-6):
    assert parts
    for p in parts:
        assert SM.signed_volume(p) > 0, p["role"]
        assert _closed(p), p["role"]
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    w, d, h = box
    assert x1 - x0 <= w + slack and y1 - y0 <= d + slack and z1 - z0 <= h + slack and z0 >= -slack
    return {p["role"] for p in parts}


def test_the_fruit_bowl_holds_real_fruit():
    box = (0.28, 0.28, 0.12)
    parts = P.kitchen_worktop_parts("fruit_bowl", *box)
    roles = _check(parts, box)
    assert {"bowl", "fruit", "stalk"} <= roles
    keys = {p["key"] for p in parts if p["role"] == "fruit"}
    assert len(keys) >= 4 and keys <= set(SM.FRUIT_KEYS.values())           # red, orange, green, the yellow lemon
    assert sum(len(p["verts"]) for p in parts) < 2500                       # dozens of items per house
    small = P.kitchen_worktop_parts("fruit_bowl", 0.2, 0.2, 0.10)            # a small bowl: no bananas over the fruit
    assert "crown" not in {p["role"] for p in small}
    bunch = SM.banana_bunch(0.0, 0.0, 0.0, 0.19)
    assert len([p for p in bunch if p["role"] == "fruit"]) == 3 and all(SM.signed_volume(p) > 0 for p in bunch)


def test_kitchen_tools_board_bottles_and_cookware():
    crock = _check(P.kitchen_worktop_parts("utensil_pot", 0.12, 0.12, 0.30), (0.12, 0.12, 0.30))
    assert {"pot", "tool", "wire"} <= crock
    board = P.kitchen_worktop_parts("chopping_board", 0.40, 0.25, 0.02)
    _check(board, (0.40, 0.25, 0.02))
    assert len(board[0]["faces"]) == 4 * 40                                 # cut through: top, bottom, rim, hole
    oil = _check(KD.styling_parts("oil_bottles", *KD.STYLING_SIZES["oil_bottles"]), KD.STYLING_SIZES["oil_bottles"])
    assert {"bottle", "contents", "spout", "cork", "salt", "lid", "tray"} <= oil
    cook = _check(KD.styling_parts("cookware", *KD.STYLING_SIZES["cookware"]), KD.STYLING_SIZES["cookware"])
    assert {"pot", "lid", "lid_rim", "knob", "handle", "pan", "rivet"} <= cook


def test_the_paper_holder_has_a_roll_with_a_core_and_a_hanging_sheet():
    parts = BT.paper_holder_parts(*BT.PAPER_HOLDER_SIZE)
    roles = _check(parts, BT.PAPER_HOLDER_SIZE)
    assert {"rosette", "arm", "cap", "flap", "roll", "core", "sheet"} <= roles
    sheet = next(p for p in parts if p["role"] == "sheet")
    roll = next(p for p in parts if p["role"] == "roll")
    assert min(v[2] for v in sheet["verts"]) < min(v[2] for v in roll["verts"]) - 0.035    # it hangs below the roll
    assert len({round(v[2], 4) for v in sheet["verts"]}) >= 3                               # a torn, zigzag edge
    assert abs(BT.paper_holder_bottom() + SM.paper_roll_z(*BT.PAPER_HOLDER_SIZE) - BT.PAPER_HOLDER_Z_M) < 1e-9


def test_the_vanity_objects_are_real_products():
    stems = BT._stems(0.0, 0.0, 0.0, 0.05, 0.16, BT.STEMS_H_M)
    assert {"vase", "stem", "plume"} <= {p["role"] for p in stems}
    assert all(SM.signed_volume(p) > 0 for p in stems)
    assert not [p for p in stems if p["role"] == "plume" and P.parts_bbox([p])[3] - P.parts_bbox([p])[0] > 0.08]
    amber = BO.pump_bottle(0.0, 0.0, 0.0, 0.033, 0.17, "terracotta", "dark")
    assert {"bottle", "contents", "label", "print", "pump", "nozzle"} <= {p["role"] for p in amber}
    # 31 Oct 2026: the amber bottle is solid amber glass with refraction (bath_objects.GLASS), the soap gel inside it
    assert next(p for p in amber if p["role"] == "bottle")["key"] == BO.GLASS["amber"]
    black = BO.pump_bottle(0.0, 0.0, 0.0, 0.033, 0.17, "dark", "handle")
    label = next(p for p in black if p["role"] == "label")
    assert max(v[1] for v in label["verts"]) < 0.0                            # on the front, not a band round it
    basin = BT._vessel(0.0, 0.0, 0.0, 0.2, 0.13, "dark")
    assert {p["role"] for p in basin} == {"basin", "drain"} and all(_closed(p) for p in basin)
    tray = SM.tray(0.0, 0.0, 0.0, 0.05, 0.08)
    assert _closed(tray) and SM.signed_volume(tray) > 0 and SM.tray_floor(0.0) > 0.0


def test_the_new_material_keys_resolve():
    from wenart.blender import furniture as F
    from wenart.polish import prompt as PR
    from wenart.style import vocabulary as V

    keys, _ = F.style_material_keys({})
    for k in list(SM.FRUIT_KEYS.values()) + [SM.OIL_KEY, SM.CARDBOARD_KEY]:
        assert k in P.MATERIAL_KEYS and k in keys, k
        slug = keys[k][0]
        assert slug in V.FLAT_COLOURS and slug in V.ROUGHNESS and slug in PR.MATERIAL_WORDS, slug
    used = set()
    for parts in (P.kitchen_worktop_parts("fruit_bowl", 0.28, 0.28, 0.12),
                  KD.styling_parts("oil_bottles", *KD.STYLING_SIZES["oil_bottles"]),
                  BT.paper_holder_parts(*BT.PAPER_HOLDER_SIZE), BT._stems(0, 0, 0, 0.05, 0.16, 0.45),
                  BO.pump_bottle(0, 0, 0, 0.033, 0.17, "terracotta", "dark")):
        used |= {P.plain_key(p["key"]) for p in parts}
    assert used <= set(P.MATERIAL_KEYS), used - set(P.MATERIAL_KEYS)
