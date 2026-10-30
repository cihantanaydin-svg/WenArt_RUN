"""30 Oct 2026, the user's review of real04 run 20261030-112241-full. UL174: "I did not like the lamp" (twice: a
"Classic ... Chandelier ... Antique Brass" and a crystal-drop "Designer chandeliers", both tagged modern by the vision
judges, hung in a modern house). UL177: "this wall texture seems to be used too much in the house, reduce it down" (an
Argus set_material walls wood_slat clad 48 wall faces of every room; four bedrooms also had slat or fluted panels).
Pure tests; real04 is only the test case."""
from wenart.blender import exterior_checks as X
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture import room_schemes as RS

STYLE = {"family": "modern", "walls": {"material": "paint", "colour": "warm greige"}}


def _lamp(title, styles=("modern",)):
    return {"id": "x", "type": "decor_pendant_light", "title": title, "styles": list(styles)}


def test_a_title_that_names_another_style_vetoes_the_judges_tags():
    classic = _lamp("Amazon Brand - Stone & Beam Classic Ceiling Pendant Chandelier Fixture, Antique Brass",
                    ("scandinavian", "modern minimal", "minimal", "modern"))
    assert C.title_styles(classic) == ["classic"]
    assert not C.styles_match(classic, "modern") and not F.decor_styles_match(classic, "modern")
    assert C.styles_match(_lamp("Classic pendant", ("classic",)), "classic")
    for title in ("5-Light Chandelier", "Designer chandeliers", "Baccarat Zenith Chandelier crystal"):
        assert not F.decor_styles_match(_lamp(title, ("minimal", "modern")), "modern"), title
    for title in ("Rivet Hugh Mid-Century Modern 3-Light Pendant Chandelier", "Mesh 4-Light Pendant Chandelier With "
                  "Edison Bulbs", "Industrial cage pendant, antique brass", "Oak lampshade (small)"):
        assert F.decor_styles_match(_lamp(title, ("industrial", "modern")), "modern"), title
    assert F.decor_styles_match({"title": "Crystal Chandelier"}, None)             # no family: no veto
    assert not F.decor_styles_match({"title": "Crystal Chandelier"}, "modern")    # untagged decor too
    assert F.STYLE_WORDS is C.STYLE_WORDS and F.STYLE_FALLBACK is C.STYLE_FALLBACK


def test_the_walls_slot_keeps_a_plain_finish():
    bad = X.validate_material_override(STYLE, {"walls": "wood_slat"})
    assert not bad["ok"] and "every wall of every room" in bad["failed"][0]
    for look in ("brick_white", "wallpaper_botanical", "tiles_subway", "stone_cladding"):
        assert not X.validate_material_override(STYLE, {"walls": look})["ok"], look
    assert X.validate_material_override(STYLE, {"kitchen_walls": "wood_veneer_oak"})["ok"]     # one room's walls
    for look in ("plaster_white", "microcement", "venetian_plaster", "concrete_exposed"):
        assert X.validate_material_override(STYLE, {"walls": look})["ok"], look
    loft = {"walls": {"material": "brick"}}                          # the brief's own brick walls
    assert X.validate_material_override(loft, {"walls": "brick_white"})["ok"]
    assert X.validate_material_override(STYLE, {"floor": "wood_herringbone_mid"})["ok"]


def _bedrooms(n, variant_level=False):
    levels = [{"id": "L0", "elevation": 0.0, "variant": "base"}]
    if variant_level:
        levels.append({"id": "L0b", "elevation": 0.0, "variant": "open plan"})
    rooms = []
    for i in range(n):
        lv = "L0b" if variant_level and i >= n // 2 else "L0"
        rooms.append({"id": f"r_{lv}_oda_{i}", "level_id": lv, "room_type": "bedroom",
                      "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]})
    furniture = [{"id": f"b{i}", "room_id": r["id"], "type": "bed_double", "level_id": r["level_id"]}
                 for i, r in enumerate(rooms)]
    return {"levels": levels, "rooms": rooms, "furniture": furniture}


def test_at_most_two_rooms_of_a_house_get_a_slat_or_fluted_wall():
    b = _bedrooms(8)
    schemes = RS.plan(b, {"family": "modern"})
    assert sum(RS.slatted(s) for s in schemes.values()) <= RS.SLAT_ROOMS_MAX
    capped = [s for s in schemes.values() if (s.get("why") or {}).get("no_slats")]
    assert capped and all(s.get("feature") in ("art_pair", "art") for s in capped)
    # a twin copies its partner's scheme: the pair counts twice
    rid = sorted(schemes)[0]
    partners = {r["id"]: rid for r in b["rooms"][1:3]}
    paired = RS.plan(b, {"family": "modern"}, partners=partners)
    assert sum(RS.slatted(s) for s in paired.values()) <= RS.SLAT_ROOMS_MAX


def test_a_variant_level_is_its_own_version_of_the_house():
    schemes = RS.plan(_bedrooms(8, variant_level=True), {"family": "modern"})
    base = sum(RS.slatted(s) for s in schemes.values() if s["level_id"] == "L0")
    variant = sum(RS.slatted(s) for s in schemes.values() if s["level_id"] == "L0b")
    assert base <= RS.SLAT_ROOMS_MAX and base + variant <= 2 * RS.SLAT_ROOMS_MAX


def test_one_stone_per_house():
    """UL204 ("Texture on the wall was also weird"): Argus put a light sandstone brick on the plinth and the plot walls
    under a ledgestone base."""
    modern = {"family": "modern"}
    bad = X.validate_material_override(modern, {"plinth": "stone_wall_ashlar", "plot_wall": "stone_wall_ashlar"})
    assert not bad["ok"] and len(bad["failed"]) == 2 and "one stone per house" in bad["failed"][0]
    assert X.validate_material_override(modern, {"plinth": "stone_wall_ledgestone"})["ok"]
    assert X.validate_material_override(modern, {"plot_wall": "plaster_white"})["ok"]          # not a stone: free
    named = {"family": "modern", "exterior": {"plinth": {"material": "stone_wall_ashlar", "source": "brief"}}}
    assert X.validate_material_override(named, {"plinth": "stone_wall_ashlar"})["ok"]
