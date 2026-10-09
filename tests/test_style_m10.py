"""Milestone 10 style profile (wenart/style/profile.py, docs/milestone10.md §4.1, §4.10, §5 row 7; track C).

Phrase parsing with objects ("cream pots" colours the pots, never the walls), colours with modifiers, the new slots,
the real02 brief (no unmatched term), the schema and the example, the profiles of every committed project (the old
slots unchanged) and the assets a profile needs.
"""
import copy
import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from wenart.style import colours as C
from wenart.style import finishes as FIN
from wenart.style import objects as O_TABLES
from wenart.style import profile as P
from wenart.style import vocabulary as V
from wenart.style.__main__ import main as style_main

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
SCHEMA = json.loads((ROOT / "wenart" / "schema" / "style.schema.json").read_text(encoding="utf-8"))
EXAMPLE = ROOT / "docs" / "examples" / "style_m10.example.json"
REAL02 = (PROJECTS / "real02" / "brief.yaml")


VALIDATOR = jsonschema.Draft202012Validator(SCHEMA)


def errors(profile) -> list[str]:
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in VALIDATOR.iter_errors(profile)]


def prof(text, **kw):
    return P.profile_from_text(text, **kw)


def real02():
    return P.profile_from_brief(yaml.safe_load(REAL02.read_text(encoding="utf-8")))


def warned(profile, *fragments) -> bool:
    return any(all(f in w for f in fragments) for w in profile["warnings"])


# --------------------------------------------------------------------------
# Phrases and objects
# --------------------------------------------------------------------------

def test_phrases_split_at_commas_and_semicolons_outside_brackets():
    text = "many large indoor plants (palms, monstera; ferns) in rattan and cream pots, cream and mustard cushions;\nwarm daylight"
    assert P.split_phrases(text) == ["many large indoor plants (palms, monstera; ferns) in rattan and cream pots",
                                     "cream and mustard cushions", "warm daylight"]
    assert P.split_phrases("a, b ; c\n d") == ["a", "b", "c", "d"]
    assert P.split_phrases("") == [] and P.split_phrases(" , ; ") == []
    assert P.split_phrases("sofa [grey, linen], rug") == ["sofa [grey, linen]", "rug"]
    assert P.split_phrases("one (unbalanced, two") == ["one (unbalanced, two"]          # a bracket never closed keeps the rest


def test_a_colour_applies_to_the_object_of_its_phrase_only():
    """"cream pots" never colours the walls; a bare colour phrase stays the wall colour (Milestone 3)."""
    p = prof("white walls, cream pots")
    assert p["walls"] == {"material": "plaster_white", "asset": "white_plaster_02", "colour": None}        # the slug is white already
    assert p["colours"]["walls"] == ["white"] and p["decor"]["pots"] == [{"material": None, "colour": "cream"}]
    p = prof("cream pots, oak floor")
    assert p["walls"]["material"] == "plaster_white" and p["walls"]["colour"] is None            # default walls, not cream
    assert warned(p, "assumed: walls plaster_white")
    p = prof("sage")                                                                             # a bare colour phrase: the wall colour
    assert p["walls"]["material"] == "paint" and p["walls"]["colour"] == "sage"
    p = prof("cream")
    assert p["walls"]["material"] == "plaster_cream" and p["walls"]["colour"] is None            # the Milestone 3 slug stays, no extra colour
    p = prof("warm white")                                                                       # a modifier makes it paint, not plaster_white
    assert p["walls"]["material"] == "paint" and p["walls"]["colour"] == "warm white"
    p = prof("mustard cushions, teal throws, sage curtains, grey rug")
    assert p["walls"]["colour"] is None
    assert p["decor"]["cushion_colours"] == ["mustard"] and p["decor"]["throw_colours"] == ["teal"]
    assert p["decor"]["curtain_colour"] == "sage" and p["decor"]["rug_colours"] == ["grey"]
    assert p["colours"] == {"cushions": ["mustard"], "throws": ["teal"], "curtains": ["sage"], "rug": ["grey"]}


def test_a_floor_phrase_does_not_recolour_the_walls():
    p = prof("white marble floor, brick walls")
    assert p["floor"]["material"] == "marble" and p["walls"]["material"] == "brick" and p["walls"]["colour"] is None
    assert warned(p, "colour 'white'", "only describes the floor 'marble'")
    p = prof("grey carpet")                                                                      # a colourable variant of the carpet
    assert p["floor"] == {"material": "carpet_wool", "asset": "Carpet016", "colour": "grey"}
    assert prof("carpet")["floor"]["material"] == "carpet" and prof("carpet")["floor"]["colour"] is None


def test_colour_pairs_with_and():
    p = prof("charcoal and white, oak floor")
    assert p["walls"] == {"material": "plaster_charcoal", "asset": "white_plaster_02", "colour": None}
    acc = p["wall_accent"]
    assert (acc["material"], acc["colour"], acc["room_types"]) == ("paint", "white", ["living", "bedroom"])
    assert "behind the sofa or the bed head" in acc["rule"] and warned(p, "accent wall colour white")
    p = prof("warm greige walls with one sage accent wall")
    assert p["walls"]["colour"] == "warm greige" and p["wall_accent"]["colour"] == "sage"
    p = prof("sage accent wall")                                                                 # the accent alone: the main walls stay open
    assert p["wall_accent"]["colour"] == "sage" and p["walls"]["colour"] is None
    p = prof("cream and mustard cushions, grey and white throws")
    assert p["decor"]["cushion_colours"] == ["cream", "mustard"] and p["decor"]["throw_colours"] == ["grey", "white"]
    p = prof("greige, sage, clay")                                                               # three colour phrases: first wins, the rest noted
    assert p["walls"]["colour"] == "greige" and warned(p, "ignored wall colour 'sage'", "walls already greige")


def test_modifiers_are_part_of_the_colour_phrase():
    p = prof("pale sage walls, warm light grey sofa, dark bronze window frames")
    assert p["walls"]["colour"] == "pale sage"
    assert p["furniture"]["by_type"]["sofa"]["fabric_colour"] == "warm light grey"
    assert p["window_frame"]["material"] == "dark_bronze" and p["window_frame"]["colour"] is None
    for colour in ("pale sage", "warm light grey", "dark bronze"):
        assert C.known(colour)
    assert prof("Sage Green walls")["walls"]["colour"] == "sage"                                 # the alias is resolved
    assert prof("gray walls")["walls"]["colour"] == "grey"
    p = prof("light walls")                                                                      # a modifier with no colour word is listed
    assert p["unmatched_terms"] == ["light walls"] and warned(p, "unmatched 'light walls'")


def test_unknown_words_are_listed_never_guessed():
    p = prof("zorple walls")
    assert p["unmatched_terms"] == ["zorple walls"] and p["walls"]["material"] == "plaster_white" and warned(p, "assumed: walls")
    assert warned(p, "unmatched 'zorple walls':", "no known material, colour or finish word")
    p = prof("greige walls, xyzzy lamp")
    assert p["unmatched_terms"] == ["xyzzy lamp"] and p["walls"]["colour"] == "greige"
    p = prof("greige zorple walls")                                                              # a known phrase with one unknown word
    assert p["matched_terms"] == ["greige zorple walls"] and warned(p, "unknown word(s) 'zorple'", "not used")
    assert p["walls"]["colour"] == "greige"
    p = prof("botanical wallpaper, wallpaper")
    assert p["walls"]["material"] == "wallpaper_botanical" and p["unmatched_terms"] == ["wallpaper"]
    assert warned(p, "unmatched 'wallpaper':", "needs a pattern word")
    assert prof("something nobody understands")["unmatched_terms"] == ["something nobody understands"]


def test_the_first_phrase_wins_a_single_slot_and_later_ones_are_noted():
    p = prof("greige walls, sage walls, oak floor, marble floor")
    assert p["walls"]["colour"] == "greige" and p["floor"]["material"] == "wood_oak_light"
    assert warned(p, "ignored wall colour 'sage'", "walls already greige") and warned(p, "ignored floor 'marble'")
    p = prof("oak doors, walnut doors")
    assert p["door"]["material"] == "wood_oak_light" and warned(p, "ignored door material")


# --------------------------------------------------------------------------
# The slots
# --------------------------------------------------------------------------

def test_floors_and_walls_of_the_new_tables():
    cases = {"whitewashed oak floor": "wood_oak_whitewashed", "natural oak floor": "wood_oak_natural", "smoked oak floor": "wood_oak_smoked",
             "grey oak floor": "wood_oak_grey", "wide plank floor": "wood_wide_plank", "light herringbone floor": "wood_herringbone_light",
             "dark chevron floor": "wood_chevron_dark", "bamboo floor": "wood_bamboo", "terrazzo floor": "terrazzo",
             "travertine floor": "travertine", "limestone floor": "limestone", "slate floor": "slate_floor",
             "cement tiles": "tiles_cement", "hexagon tiles": "tiles_hexagon", "vinyl floor": "vinyl", "cork floor": "cork",
             "sisal floor": "sisal", "large format tiles": "tiles_large_porcelain"}
    for text, slug in cases.items():
        p = prof(text)
        assert p["floor"]["material"] == slug, text
        assert errors(p) == [], text
    # the old words keep their old slugs
    assert prof("oak floor")["floor"]["material"] == "wood_oak_light" and prof("herringbone")["floor"]["material"] == "wood_parquet"
    walls = {"lime plaster walls": "lime_plaster", "venetian plaster walls": "venetian_plaster", "microcement walls": "microcement",
             "wood slat walls": "wood_slat", "stacked stone wall": "stone_wall_ledgestone", "rubble stone walls": "stone_wall_rubble",
             "white brick walls": "brick_white", "grey brick walls": "brick_grey", "reclaimed brick walls": "brick_reclaimed",
             "exposed concrete walls": "concrete_exposed", "stripe wallpaper": "wallpaper_stripe", "wallpaper herringbone": "wallpaper_herringbone",
             "grasscloth walls": "wallpaper_grasscloth", "brick walls": "brick", "painted walls": "paint"}
    for text, slug in walls.items():
        assert prof(text)["walls"]["material"] == slug, text
    p = prof("sage botanical wallpaper")
    assert p["walls"] == {"material": "wallpaper_botanical", "asset": None, "colour": "sage"}       # a procedural look: no asset
    p = prof("white brick walls")                                                                    # flat mode takes a colour, a photo look keeps its own
    assert p["walls"]["colour"] is None and warned(prof("greige brick walls"), "only describes the wall finish 'brick'")
    assert prof("greige lime plaster walls")["walls"]["colour"] == "greige"
    assert prof("greige plaster walls")["walls"] == {"material": "plaster_white", "asset": "white_plaster_02", "colour": "greige"}


def test_wet_walls_tile_size_and_grout():
    p = prof("white subway tiles in the bathroom with dark grey grout, 7.5 x 15 cm")
    assert p["wet_walls"] == {"material": "tiles_subway", "asset": None, "tile_size_m": [0.15, 0.075], "pattern": "running_bond",
                              "colour": "white", "grout_colour": "dark grey"}
    assert p["colours"]["wet_walls"] == ["white", "dark grey"]
    p = prof("zellige bathroom tiles")
    assert p["wet_walls"]["material"] == "tiles_zellige" and p["wet_walls"]["tile_size_m"] == [0.1, 0.1] and p["wet_walls"]["pattern"] == "grid"
    p = prof("60x120 cm porcelain shower tiles with black grout")
    assert p["wet_walls"]["tile_size_m"] == [0.6, 1.2] and p["wet_walls"]["grout_colour"] == "black"
    assert prof("marble slab bathroom walls")["wet_walls"]["material"] == "marble_slab"
    p = prof("oak floor")                                                                            # no word: the default wet-wall tile
    assert p["wet_walls"] == {"material": "tiles_light", "asset": None, "tile_size_m": None, "pattern": None,
                              "colour": None, "grout_colour": None}
    assert P.room_surfaces(prof("zellige bathroom tiles"), "bathroom")["walls"] == "tiles_zellige"


def test_doors_handles_cabinets_worktops():
    p = prof("black shaker doors with brass handles")
    assert p["door"] == {"material": "lacquer_dark", "asset": None, "style": "shaker_panel", "colour": "black", "handle": "brass"}
    assert p["cabinets"]["handle"] is None                                                           # the handles belong to the doors here
    p = prof("white shaker kitchen with brass handles and oak worktop")
    assert p["cabinets"] == {"front_style": "shaker", "colour": "white", "handle": "brass", "worktop": "wood", "wood": None}
    assert p["door"]["handle"] is None
    p = prof("oak kitchen, black handles")                                                           # a phrase of its own: kitchen and doors
    assert p["cabinets"]["wood"] == "wood_veneer_oak" and p["cabinets"]["handle"] == "black" and p["door"]["handle"] == "black"
    p = prof("grey slatted cabinets, stone worktops, brushed steel handles")
    assert (p["cabinets"]["front_style"], p["cabinets"]["colour"], p["cabinets"]["worktop"], p["cabinets"]["handle"]) == \
        ("slatted", "grey", "stone", "brushed_steel")
    p = prof("sage doors")                                                                           # any colour: a painted leaf
    assert p["door"]["material"] == "painted_wood_white" and p["door"]["colour"] == "sage"
    p = prof("oak doors")
    assert p["door"]["material"] == "wood_oak_light" and p["door"]["colour"] is None
    p = prof("brass handles")                                                                        # no other object: kitchen and doors both
    assert p["cabinets"]["handle"] == "brass" and p["door"]["handle"] == "brass"
    for text in ("barn doors", "sliding doors", "pocket doors", "glazed doors", "double doors", "entrance door", "flush doors"):
        assert prof(text)["door"]["style"] in FIN.DOOR_STYLES, text


def test_window_frames_and_the_outside_copy():
    cases = {"dark bronze window frames": ("dark_bronze", None), "anthracite window frames": ("aluminium_anthracite", None),
             "white window frames": ("pvc_white", None), "black steel windows": ("steel_black", None),
             "oak window frames": ("oak", None), "sage window frames": ("painted_metal_white", "sage"),
             "white aluminium window frames": ("painted_metal_white", "white"), "pvc window frames": ("pvc_white", None),
             "warm white window frames": ("painted_metal_white", "warm white")}
    for text, (material, colour) in cases.items():
        p = prof(text)
        assert (p["window_frame"]["material"], p["window_frame"]["colour"]) == (material, colour), text
        assert p["window_frame"]["outside"] == {"material": material, "colour": colour}, text      # inside and outside
    assert prof("oak floor")["window_frame"]["material"] == "painted_metal_white"                   # the old default stays


def test_furniture_decor_and_accents():
    p = prof("light grey fabric sofa, glass coffee table, rattan armchair, white wardrobe, marble dining table")
    by = p["furniture"]["by_type"]
    assert by["sofa"] == by["sofa_corner"] == {"fabric_colour": "light grey", "colour": None, "material_tags": ["fabric"]}
    assert by["table_coffee"] == {"fabric_colour": None, "colour": None, "material_tags": ["glass"]}
    assert by["armchair"]["material_tags"] == ["rattan"] and by["wardrobe"]["colour"] == "white" and by["table_dining"]["material_tags"] == ["marble"]
    p = prof("natural light wood furniture")
    assert p["furniture"]["wood"] == "wood_veneer_oak_light" and p["colours"] == {}
    for text, slug in {"walnut furniture": "wood_veneer_walnut", "dark oak furniture": "wood_veneer_black_oak",
                       "oak furniture": "wood_veneer_oak", "ash furniture": "wood_veneer_ash", "teak furniture": "wood_veneer_teak"}.items():
        assert prof(text)["furniture"]["wood"] == slug and slug in V.FURNITURE_MATERIALS
    p = prof("mustard and teal accents, brass details")
    assert p["furniture"]["accents"] == ["mustard", "teal", "brass"]
    p = prof("grey upholstery")
    assert p["furniture"]["fabric_colour"] == "grey"
    p = prof("white furniture")                                                                      # no furniture-wide colour slot: listed
    assert p["unmatched_terms"] == ["white furniture"] and warned(p, "no furniture-wide colour slot")
    p = prof("palms and ferns, a few olive trees")
    assert p["decor"]["plant_species"] == ["palm", "fern", "olive"] and p["decor"]["plant_amount"] == "few"
    p = prof("many fiddle leaf fig plants in terracotta pots, cream ceramic planters")
    assert p["decor"]["plant_species"] == ["fiddle_leaf_fig"]
    assert p["decor"]["pots"] == [{"material": "terracotta", "colour": None}, {"material": "ceramic", "colour": "cream"}]


def test_the_natural_style_word_assumes_light_wood_only_when_no_wood_is_named():
    p = prof("Modern natural")
    assert p["family"] == "modern" and p["style_tags"] == ["natural"] and p["unmatched_terms"] == []
    assert p["furniture"]["wood"] == "wood_veneer_oak_light"
    assert warned(p, "assumed: furniture wood wood_veneer_oak_light", "'natural'")
    p = prof("Modern natural, walnut furniture")
    assert p["furniture"]["wood"] == "wood_veneer_walnut" and not warned(p, "assumed: furniture wood")


def test_lighting_moods_and_their_notes():
    for text, mood in {"bright noon": "bright noon", "midday sun": "bright noon", "blue hour": "blue hour", "twilight": "blue hour",
                       "soft cloudy light": "cloudy soft", "interior evening": "interior evening", "lamps on": "interior evening",
                       "golden evening light": "golden evening", "daylight": "warm daylight", "bright daylight": "bright noon"}.items():
        assert prof(text)["lighting"]["mood"] == mood, text
    p = prof("interior evening")
    assert p["lighting"]["hdri"] == "sunset_jhbcentral" and warned(p, "lamps are on")
    assert warned(prof("blue hour"), "blue hour mood: no sun") and warned(prof("night"), "night mood: no sun")
    assert not warned(prof("bright noon"), "no sun")


# --------------------------------------------------------------------------
# The exterior slots
# --------------------------------------------------------------------------

def test_exterior_fallback_is_assumed_and_listed():
    p = prof("greige walls, dark bronze window frames")
    ext = p["exterior"]
    assert (ext["facade"]["material"], ext["facade"]["colour"], ext["facade"]["source"], ext["facade"]["assumed"]) == \
        ("render", "greige", "fallback", True)                                                       # the interior wall colour as smooth render
    assert (ext["roof"]["material"], ext["roof"]["colour"], ext["roof"]["assumed"]) == ("concrete_tiles", "anthracite", True)
    assert (ext["paving"]["material"], ext["paving"]["colour"]) == ("paving", "grey") and ext["garden"]["material"] == "grass"
    assert (ext["window_frame"]["material"], ext["window_frame"]["source"], ext["window_frame"]["assumed"]) == ("dark_bronze", "style", False)
    assert (ext["door"]["source"], ext["door"]["assumed"]) == ("fallback", True)                      # the interior door seen from outside
    assert warned(p, "assumed: exterior facade render in greige", "roof concrete_tiles in anthracite", "door as inside",
                  "style.exterior_fallback")
    assert "window_frame as inside" not in " ".join(p["warnings"])
    assert p["exterior_fallback"] == P.BUILTIN_DEFAULTS["style"]["exterior_fallback"]
    for look in ext.values():
        assert V.MATERIALS[look["material"]] and look["asset"] == P.asset_of(look["material"])


def test_the_exterior_words_of_the_brief_win_over_style_and_fallback():
    brief = {"style": "greige walls, brick facade", "exterior": {"facade": "stone cladding", "roof": "clay tiles", "window_frame": "black steel",
                                                                 "door": "walnut", "paving": "gravel", "garden": "", "bogus": "x"}}
    p = P.profile_from_brief(brief)
    ext = p["exterior"]
    assert (ext["facade"]["material"], ext["facade"]["source"], ext["facade"]["assumed"]) == ("stone_cladding", "brief", False)
    assert ext["roof"]["material"] == "clay_tiles" and ext["window_frame"]["material"] == "steel_black"
    assert ext["door"]["material"] == "wood_walnut" and ext["paving"]["material"] == "gravel"
    assert ext["garden"] == {"material": "grass", "asset": "Grass004", "colour": None, "source": "fallback", "assumed": True}
    assert warned(p, "ignored exterior word 'bogus: x'") and warned(p, "assumed: exterior garden grass")
    assert p["window_frame"]["material"] == "painted_metal_white"                                    # the exterior words never change the inside
    # a word with no known material falls through to the next source, listed
    p = P.profile_from_brief({"style": "oak floor", "exterior": {"facade": "mysterious material", "roof": "slate"}})
    assert p["exterior"]["facade"]["source"] == "fallback" and p["exterior"]["roof"]["material"] == "slate"
    assert warned(p, "unmatched exterior.facade 'mysterious material'")
    # the style text's own exterior words
    p = prof("slate roof, brick facade, gravel paving, lawn")
    ext = p["exterior"]
    assert (ext["roof"]["material"], ext["facade"]["material"], ext["paving"]["material"], ext["garden"]["material"]) == \
        ("slate", "brick_red", "gravel", "grass") and ext["roof"]["source"] == "brief"
    # the exterior block is read for every style of the brief
    both = P.profiles_from_brief({"styles": ["oak floor", "marble floor"], "exterior": {"roof": "zinc"}})
    assert [x["exterior"]["roof"]["material"] for x in both] == ["standing_seam", "standing_seam"]


# --------------------------------------------------------------------------
# real02 (acceptance row 7) and the committed projects
# --------------------------------------------------------------------------

def test_real02_has_no_unmatched_term_and_the_target_slots(capsys):
    p = real02()
    assert p["unmatched_terms"] == [] and len(p["matched_terms"]) == 10
    assert p["family"] == "modern" and p["style_tags"] == ["natural"] and p["lighting"]["mood"] == "warm daylight"
    assert p["floor"] == {"material": "wood_oak_light", "asset": "WoodFloor051", "colour": None}
    assert p["walls"] == {"material": "paint", "asset": "plastered_wall", "colour": "warm greige"}     # not plaster_cream (the old bug)
    assert p["wall_accent"] is None
    sofa = p["furniture"]["by_type"]["sofa"]
    assert sofa["fabric_colour"] == "light grey" and sofa["material_tags"] == ["fabric"] and p["furniture"]["by_type"]["sofa_corner"] == sofa
    assert p["furniture"]["wood"] == "wood_veneer_oak_light"
    assert p["furniture"]["by_type"]["table_coffee"]["material_tags"] == ["glass"]
    assert p["decor"] == {"plant_species": ["palm", "monstera", "fern"], "plant_amount": "many",
                          "pots": [{"material": "rattan", "colour": None}, {"material": None, "colour": "cream"}],
                          "cushion_colours": ["cream", "mustard"], "throw_colours": [], "curtain_colour": None, "rug_colours": []}
    assert p["window_frame"] == {"material": "dark_bronze", "asset": None, "colour": None,
                                 "outside": {"material": "dark_bronze", "colour": None}}
    assert p["colours"] == {"walls": ["warm greige"], "sofa": ["light grey"], "pots": ["cream"], "cushions": ["cream", "mustard"],
                            "window_frames": ["dark bronze"]}
    assert p["exterior"]["facade"]["colour"] == "warm greige" and p["exterior"]["window_frame"]["material"] == "dark_bronze"
    assert not [w for w in p["warnings"] if "unknown word" in w or w.startswith("unmatched")]
    assert errors(p) == []


def test_real02_cli_prints_no_unmatched(tmp_path, capsys):
    assert style_main([str(PROJECTS / "real02"), "--out", str(tmp_path / "style.json")]) == 0
    out = capsys.readouterr().out
    assert "unmatched" not in out.replace("assumed", "") and "walls paint" in out
    written = json.loads((tmp_path / "style.json").read_text(encoding="utf-8"))
    assert written == real02() and errors(written) == []


def test_the_example_is_the_real02_profile_and_validates():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert errors(example) == []
    assert example == real02(), "regenerate: python -m wenart.style projects/real02 --out docs/examples/style_m10.example.json"
    jsonschema.Draft202012Validator.check_schema(SCHEMA)


@pytest.mark.parametrize("mutate", [
    lambda p: p["walls"].update(colour="Greige!"),                        # not a colour phrase
    lambda p: p["walls"].pop("asset"),
    lambda p: p["cabinets"].update(front_style="ornate"),
    lambda p: p["decor"].update(plant_species=["cactus"]),
    lambda p: p["door"].update(style="revolving"),
    lambda p: p["exterior"]["roof"].update(source="guess"),
    lambda p: p["exterior"]["roof"].update(assumed=False),                # the fallback is always assumed
    lambda p: p["exterior"].pop("garden"),
    lambda p: p["lighting"].update(mood="sunny"),
    lambda p: p.update(extra_slot={}),
    lambda p: p["wet_walls"].update(pattern="spiral"),
    lambda p: p["furniture"]["by_type"]["sofa"].update(material_tags=["plastic"]),
    lambda p: p["furniture"].update(wood="oak"),
    lambda p: p.update(wall_accent={"material": "paint"}),                # an accent wall needs its colour, rule and room types
])
def test_broken_copies_of_the_example_fail(mutate):
    broken = copy.deepcopy(json.loads(EXAMPLE.read_text(encoding="utf-8")))
    mutate(broken)
    assert errors(broken), "the schema accepted a broken profile"


OLD_SLOTS = {   # (floor, walls, light, family) of every committed brief at the start commit of Milestone 10
    "synthetic-01": [("wood_oak_light", "plaster_white", "warm daylight", "scandinavian")],
    "synthetic-03": [("concrete_polished", "plaster_charcoal", "cool daylight", "modern minimal"),
                     ("terracotta", "plaster_cream", "golden evening", "mediterranean")],
    "synthetic-04": [("wood_walnut", "plaster_cream", "warm daylight", "japandi")],
    "synthetic-05": [("wood_oak_light", "plaster_white", "warm daylight", "modern")],
    "synthetic-06": [("wood_walnut", "plaster_white", "warm daylight", "modern")],
}


def test_every_committed_project_has_a_valid_profile_and_the_old_slots_are_unchanged():
    briefs = sorted(PROJECTS.glob("*/brief.yaml"))
    assert {b.parent.name for b in briefs} >= set(OLD_SLOTS) | {"real02"}
    for brief_path in briefs:
        brief = yaml.safe_load(brief_path.read_text(encoding="utf-8"))
        profiles = P.profiles_from_brief(brief)
        for p in profiles:
            assert errors(p) == [], brief_path.parent.name
            for slug in P.material_slugs(p):
                assert slug in V.FLAT_COLOURS, (brief_path.parent.name, slug)
            assert V.LIGHTING[p["lighting"]["mood"]]["hdri"] == p["lighting"]["hdri"]
        name = brief_path.parent.name
        if name in OLD_SLOTS:
            got = [(p["floor"]["material"], p["walls"]["material"], p["lighting"]["mood"], p["family"]) for p in profiles]
            assert got == OLD_SLOTS[name], name
    assert errors(P.default_profile()) == [] and errors(P.profile_from_brief(None)) == []        # a project with no brief (real01)


def test_what_changes_in_the_committed_projects_is_only_what_the_old_tables_ignored():
    """real02: walls plaster_cream (from "cream pots") -> warm greige paint, dark bronze frames; synthetic-03 (charcoal and white),
    -05 and -06: brass details / mustard and teal accents match (accents), charcoal and white adds an accent wall."""
    load = lambda n: P.profiles_from_brief(yaml.safe_load((PROJECTS / n / "brief.yaml").read_text(encoding="utf-8")))
    s3 = load("synthetic-03")
    assert s3[0]["wall_accent"]["colour"] == "white" and s3[0]["furniture"]["accents"] == ["brass"] and s3[0]["unmatched_terms"] == []
    assert s3[1]["wall_accent"] is None and s3[1]["unmatched_terms"] == ["rattan and linen"]
    assert load("synthetic-05")[0]["furniture"]["accents"] == ["brass"] and load("synthetic-05")[0]["unmatched_terms"] == ["linen textiles"]
    assert load("synthetic-06")[0]["furniture"]["accents"] == ["mustard", "teal"] and load("synthetic-06")[0]["unmatched_terms"] == []
    for name in ("synthetic-01", "synthetic-04"):
        p = load(name)[0]
        assert p["wall_accent"] is None and p["furniture"]["accents"] == [] and p["window_frame"]["material"] == "painted_metal_white"


# --------------------------------------------------------------------------
# Assets and helpers
# --------------------------------------------------------------------------

def test_assets_in_profile_skip_procedural_looks_and_find_the_new_slots():
    p = prof("subway tiles in the bathroom, sage botanical wallpaper, oak kitchen with stone worktop, natural light wood furniture, "
             "rattan pots, slate roof, gravel paving, terrazzo floor, dark bronze window frames")
    assets = P.assets_in_profile(p)
    by_slug = {slug: (source, asset) for source, asset, slug in assets["textures"]}
    assert "tiles_subway" not in by_slug and "wallpaper_botanical" not in by_slug and "dark_bronze" not in by_slug   # procedural
    assert by_slug["terrazzo"] == ("polyhaven", "terrazzo_tiles") and by_slug["slate"] == ("polyhaven", "roof_slates_03")
    assert by_slug["rattan"] == ("ambientcg", "Wicker005") and by_slug["wood_veneer_oak"][0] == "polyhaven"
    assert by_slug["wood_veneer_oak_light"] == ("polyhaven", "oak_veneer_02") and "stone_worktop" not in by_slug   # a flat worktop has no file
    assert len({a for _, a, _ in assets["textures"]}) == len(assets["textures"])
    assert assets["hdris"] == [("polyhaven", "kloppenheim_06")]
    # the real02 profile needs the plastered wall, the oak floor, the grey render, the anthracite concrete roof ...
    ids = {a for _, a, _ in P.assets_in_profile(real02())["textures"]}
    assert {"plastered_wall", "WoodFloor051", "grey_plaster", "grey_roof_01", "large_square_pattern_01", "Grass004", "Wicker005",
            "oak_veneer_02"} <= ids
    assert P.material_slugs(real02())[:3] == ["wood_oak_light", "paint", "plaster_white"]


def test_a_partial_older_profile_still_lists_its_assets():
    """A style.json of Milestone 3-9 has none of the new slots (and may lack some old ones): material_slugs and
    assets_in_profile read what is there."""
    old = {"floor": {"material": "wood_oak_light", "asset": "WoodFloor051"}, "walls": {"material": "plaster_white", "asset": "white_plaster_02"},
           "lighting": {"hdri": "kloppenheim_06"}}
    assert P.material_slugs(old) == ["wood_oak_light", "plaster_white"]
    assert P.assets_in_profile(old) == {"textures": [("ambientcg", "WoodFloor051", "wood_oak_light"),
                                                     ("polyhaven", "white_plaster_02", "plaster_white")],
                                        "hdris": [("polyhaven", "kloppenheim_06")]}
    assert P.assets_in_profile({}) == {"textures": [], "hdris": []}


def test_helpers_colourable_and_wet_safe():
    assert P.is_colourable("paint") and P.is_colourable("plaster_white") and P.is_colourable("tiles_subway") and P.is_colourable("render")
    assert not P.is_colourable("brick") and not P.is_colourable("wood_oak_light") and not P.is_colourable("wood_oak_whitewashed")
    assert not P.is_colourable("dark_bronze") and not P.is_colourable("nonsense")
    assert P.is_wet_safe("tiles_light") and P.is_wet_safe("terrazzo") and not P.is_wet_safe("wood_oak_light")
    assert prof("terrazzo floor")["wet_floor"]["material"] == "terrazzo" and prof("oak floor")["wet_floor"]["material"] == "tiles_light"
    assert P.asset_of("tiles_subway") is None and P.asset_of("wood_veneer_walnut") == "walnut_veneer" and P.source_of("tiles_subway") == "procedural"
    assert prof("vinyl floor")["wet_floor"]["colour"] is None and prof("sage vinyl")["floor"]["colour"] == "sage"


def test_match_text_keeps_its_old_contract():
    scan = P.match_text("Scandinavian, light oak floor, white walls, warm daylight")
    assert {"floor", "walls", "light", "family", "matched", "unmatched", "notes"} <= set(scan)
    assert (scan["floor"], scan["walls"], scan["light"], scan["family"]) == ("wood_oak_light", "plaster_white", "warm daylight", "scandinavian")
    assert scan["reasons"] == {} and "wall_accent" in scan["draft"]
    assert P.match_text("")["unmatched"] == [] and P.match_text("Modern, oak")["family"] == "modern"


def test_photo_terms_fill_only_open_slots_and_never_set_a_colour():
    terms = {"terms": [{"slot": "floor", "value": "marble", "files": ["a.jpg"]}, {"slot": "walls", "value": "plaster_charcoal", "files": ["a.jpg"]}]}
    p = P.profile_from_text("greige walls", photo_terms=terms)
    assert p["walls"]["colour"] == "greige" and p["floor"]["material"] == "marble" and p["floor"]["colour"] is None
    p = P.profile_from_text("oak floor", photo_terms=terms)
    assert p["walls"] == {"material": "plaster_charcoal", "asset": "white_plaster_02", "colour": None}
    assert errors(p) == []


def test_exterior_look_from_words_is_public_and_strict():
    look, notes = P.exterior_look_from_words("facade", "smooth render in warm greige")
    assert look == {"material": "render", "colour": "warm greige"} and notes == []
    assert P.exterior_look_from_words("roof", "anthracite concrete tiles")[0] == {"material": "concrete_tiles", "colour": "anthracite"}
    assert P.exterior_look_from_words("window_frame", "dark bronze")[0] == {"material": "dark_bronze", "colour": None}
    assert P.exterior_look_from_words("door", "walnut")[0] == {"material": "wood_walnut", "colour": None}
    assert P.exterior_look_from_words("garden", "mysterious")[0] is None
    with pytest.raises(ValueError):
        P.exterior_look_from_words("chimney", "brick")


def test_the_default_profile_block_of_defaults_yaml_is_current():
    block = yaml.safe_load(P.default_block_yaml())
    assert block == P.load_defaults()["style"]["profile"]


def test_empty_brackets_and_odd_input_never_crash():
    for text in ("sofa (), grey", "walls []", "plants (palms,), ()", "( ) ( )", "(", ")", "grey ((nested)) walls", "ünïcode façade, béton brut walls", "   ",
                 None, ""):
        p = P.profile_from_text(text)
        assert errors(p) == [], text
    assert P.profile_from_text("grey ((nested)) walls")["walls"]["colour"] == "grey"
    assert P.profile_from_text("ünïcode façade, béton brut walls")["walls"]["material"] == "concrete_exposed"


def test_random_briefs_validate_and_are_deterministic():
    """A seeded fuzz: 150 random phrases made of the words of every table never crash, always validate against the schema and
    give the same profile twice."""
    import random

    rng = random.Random(20261008)
    words = (list(C.colour_words()) + [w for w, _ in O_TABLES.OBJECT_WORDS] + [w for w, _ in V.FLOOR_WORDS] + [w for w, _ in V.WALL_WORDS]
             + [w for w, _ in V.LIGHT_WORDS] + [k for k, _ in V.STYLE_FAMILIES] + list(C.MODIFIERS) + sorted(O_TABLES.DESCRIPTORS)
             + [w for t in O_TABLES.EXTERIOR_WORDS.values() for w, _ in t] + [w for w, _ in O_TABLES.WET_WALL_WORDS]
             + [w for w, _ in O_TABLES.HANDLE_WORDS] + [w for w, _ in O_TABLES.DOOR_STYLE_WORDS]
             + ["60x120", "7.5 x 15 cm", "grout", "natural", "(palms, ferns)", "[x]", "zorple", "123", "é", "()", "-", ","])
    for _ in range(150):
        phrases = [" ".join(rng.choice(words) for _ in range(rng.randint(1, 7))) for _ in range(rng.randint(1, 5))]
        text = rng.choice([", ", "; ", "\n"]).join(phrases)
        p = P.profile_from_text(text)
        assert errors(p) == [], text
        assert P.profile_from_text(text) == p, text
        assert set(p["matched_terms"]) | set(p["unmatched_terms"]) == set(P.split_phrases(text)), text


def test_a_metal_frame_word_with_a_metal_colour_takes_that_metal():
    """'dark bronze aluminium' is the dark bronze metal frame, not white painted metal tinted dark bronze (lead fix
    after the merge of tracks C, E and F); a colour without its own metal look stays a painted metal frame."""
    from wenart.style import profile as P

    look = lambda phrase: P.exterior_look_from_words("window_frame", phrase)[0]        # noqa: E731
    assert look("dark bronze aluminium") == {"material": "dark_bronze", "colour": None}
    assert look("anthracite aluminium") == {"material": "aluminium_anthracite", "colour": None}
    assert look("black aluminium") == {"material": "steel_black", "colour": None}
    assert look("white aluminium") == {"material": "painted_metal_white", "colour": "white"}


# --------------------------------------------------------------------------
# Code review follow-up of Milestone 10 (findings #30 - #33, #35, #36 and the low plant-word finding)
# --------------------------------------------------------------------------

def test_review_30_a_compound_noun_gives_its_words_to_the_head_noun():
    """"black door handles" is black handles of the doors; the doors themselves are not black, and the handles are not
    left empty. The earlier object words of a compound are qualifiers only."""
    base = prof("")
    p = prof("black door handles")
    assert p["door"]["handle"] == "black" and p["door"]["colour"] is None and p["door"]["material"] == base["door"]["material"]
    assert p["cabinets"]["handle"] is None
    p = prof("brass cabinet handles")
    assert p["cabinets"]["handle"] == "brass" and p["cabinets"]["colour"] is None and p["door"]["handle"] is None
    p = prof("white window blinds")
    assert p["decor"]["curtain_colour"] == "white" and p["window_frame"] == base["window_frame"]
    p = prof("grey sofa cushions")
    assert p["decor"]["cushion_colours"] == ["grey"] and p["furniture"]["by_type"] == {}
    p = prof("white cabinet doors")                       # the doors of the cabinets, not the interior doors
    assert p["cabinets"]["colour"] == "white" and p["door"] == base["door"]
    p = prof("oak floor lamps")                           # a lamp, not a floor
    assert p["floor"] == base["floor"] and p["unmatched_terms"] == ["oak floor lamps"]
    p = prof("oak window sills")                          # no sill slot: listed, the window frames stay as they were
    assert p["window_frame"] == base["window_frame"] and p["unmatched_terms"] == ["oak window sills"]
    assert warned(p, "unmatched 'oak window sills':", "sill")
    p = prof("black handles")                             # one object word: unchanged
    assert p["door"]["handle"] == "black" and p["cabinets"]["handle"] == "black"
    p = prof("oak window frames, striped wallpaper walls")                  # two objects of one value are one object
    assert p["window_frame"]["material"] == "oak" and p["walls"]["material"] == "wallpaper_stripe"


def test_review_31_an_unknown_noun_never_recolours_the_walls_or_replaces_the_floor():
    """Milestone 3's bare reading (a colour is the wall colour, a floor word is the floor) is for phrases with no other
    word: an unknown noun lists the phrase and applies nothing."""
    base = prof("")
    for text, unknown in (("black bar stools", "bar"), ("emerald velvet chaise", "chaise"), ("copper pendant lights", "pendant"),
                          ("gold mirror", "mirror"), ("navy headboard", "headboard"), ("marble side table", "side"),
                          ("walnut bar stools", "bar")):
        p = prof(text)
        assert p["unmatched_terms"] == [text] and p["matched_terms"] == [], text
        for slot in ("walls", "floor", "wet_floor", "door", "wall_accent"):
            assert p[slot] == base[slot], (text, slot)
        assert p["exterior"]["facade"] == base["exterior"]["facade"], text
        assert warned(p, f"unmatched '{text}':", "unknown word", f"'{unknown}'"), text
    p = prof("sage walls, black bar stools, oak floor")           # the other phrases still apply
    assert p["walls"]["colour"] == "sage" and p["floor"]["material"] == "wood_oak_light" and p["unmatched_terms"] == ["black bar stools"]
    assert prof("gold mirror, black")["walls"]["colour"] == "black"
    # the bare phrases of Milestone 3 keep working
    assert prof("black")["walls"]["colour"] == "black" and prof("charcoal")["walls"]["material"] == "plaster_charcoal"
    assert prof("warm greige")["walls"]["colour"] == "warm greige" and prof("charcoal and white")["wall_accent"]["colour"] == "white"
    assert prof("light oak")["floor"]["material"] == "wood_oak_light" and prof("marble")["floor"]["material"] == "marble"
    assert prof("natural light oak")["floor"]["material"] == "wood_oak_light"
    p = prof("bright white, rich walnut")                                     # plain adjectives are no unknown nouns
    assert p["matched_terms"] == ["bright white", "rich walnut"] and p["floor"]["material"] == "wood_walnut"
    assert prof("fresh sage")["walls"]["colour"] == "sage" and prof("white and wood")["unmatched_terms"] == ["white and wood"]
    p = prof("modern white")                                                  # a style word beside a colour is no unknown word
    assert p["family"] == "modern" and p["walls"]["material"] == "plaster_white"


def test_review_32_a_colour_after_in_or_with_goes_to_the_finish_named_before_it():
    p = prof("painted walls in sage")
    assert p["walls"] == {"material": "paint", "asset": "plastered_wall", "colour": "sage"} and not warned(p, "ignored wall colour")
    p = prof("lime plaster walls in warm white")
    assert p["walls"]["material"] == "lime_plaster" and p["walls"]["colour"] == "warm white" and not warned(p, "ignored")
    p = prof("striped wallpaper in navy and white")
    assert p["walls"]["material"] == "wallpaper_stripe" and p["walls"]["colour"] == "navy"
    assert p["wall_accent"]["colour"] == "white" and p["wall_accent"]["material"] == "paint"
    p = prof("plaster walls in sage")
    assert p["walls"]["material"] == "plaster_white" and p["walls"]["colour"] == "sage"
    assert prof("walls in sage")["walls"]["colour"] == "sage" and prof("sage painted walls")["walls"]["colour"] == "sage"
    # a colour already given stays; a later phrase never fills the colour of an earlier phrase
    p = prof("sage painted walls in navy")
    assert p["walls"]["colour"] == "sage" and warned(p, "ignored wall colour 'navy'")
    p = prof("white walls, walls in sage")
    assert p["walls"]["colour"] is None and warned(p, "ignored")
    # a finish that keeps its photo colour takes no colour, and its accent colour is not left alone
    p = prof("exposed brick walls in navy and white")
    assert p["walls"]["material"] == "brick" and p["wall_accent"] is None
    assert warned(p, "only describes the wall finish") and warned(p, "ignored accent colour 'white'")


def test_review_33_wallpaper_on_an_accent_wall_is_the_accent_finish_not_the_walls():
    base = prof("")
    for text in ("botanical wallpaper accent wall", "accent wall in botanical wallpaper", "botanical wallpaper on the accent wall",
                 "feature wall in botanical wallpaper", "accent wall with botanical wallpaper"):
        p = prof(text)
        assert p["wall_accent"] and p["wall_accent"]["material"] == "wallpaper_botanical", text
        assert p["walls"] == base["walls"], text
    p = prof("white walls, botanical wallpaper accent wall in the bedroom")
    assert p["walls"]["material"] == "plaster_white" and p["wall_accent"]["material"] == "wallpaper_botanical"
    p = prof("white walls with botanical wallpaper on the accent wall")
    assert p["walls"]["material"] == "plaster_white" and p["wall_accent"]["material"] == "wallpaper_botanical"
    p = prof("exposed brick accent wall")                                     # the control of the review
    assert p["wall_accent"]["material"] == "brick" and p["walls"] == base["walls"]
    # wallpaper for the walls and a separate accent wall stay two things
    p = prof("striped wallpaper and a navy accent wall")
    assert p["walls"]["material"] == "wallpaper_stripe" and p["wall_accent"]["colour"] == "navy" and p["wall_accent"]["material"] == "paint"
    p = prof("striped wallpaper walls, navy accent wall")
    assert p["walls"]["material"] == "wallpaper_stripe" and p["wall_accent"]["colour"] == "navy"
    p = prof("striped wallpaper walls with a navy accent wall")
    assert p["walls"]["material"] == "wallpaper_stripe" and p["wall_accent"]["colour"] == "navy"
    p = prof("wallpaper accent wall")                                         # no pattern word: listed
    assert p["unmatched_terms"] == ["wallpaper accent wall"] and p["walls"] == base["walls"] and p["wall_accent"] is None


def test_review_35_an_exterior_door_is_style_sourced_only_when_the_brief_named_its_material():
    for text in ("black handles", "sliding doors"):
        p = prof(text)
        door = p["exterior"]["door"]
        assert door["source"] == "fallback" and door["assumed"] is True, text
        assert warned(p, "assumed: exterior", "door as inside"), text
    for text in ("oak doors", "black doors"):
        door = prof(text)["exterior"]["door"]
        assert door["source"] == "style" and door["assumed"] is False, text
    p = prof("sliding doors, black handles, anthracite window frames")
    assert p["exterior"]["door"]["assumed"] is True and p["exterior"]["window_frame"]["source"] == "style"


def test_review_36_a_tile_size_without_a_unit_is_read_by_what_is_plausible_and_listed():
    assert O_TABLES.tile_sizes("600x1200")[0][0] == [0.6, 1.2] and O_TABLES.tile_sizes("60x120")[0][0] == [0.6, 1.2]
    assert O_TABLES.tile_sizes("300x300")[0][0] == [0.3, 0.3] and O_TABLES.tile_sizes("10x10")[0][0] == [0.1, 0.1]
    assert O_TABLES.tile_sizes("60x120 cm")[0][0] == [0.6, 1.2] and O_TABLES.tile_sizes("600x1200 mm")[0][0] == [0.6, 1.2]
    p = prof("600x1200 porcelain bathroom tiles")
    assert p["wet_walls"]["tile_size_m"] == [0.6, 1.2] and warned(p, "assumed: tile size '600x1200'", "mm", "no unit")
    p = prof("60x120 porcelain bathroom tiles")
    assert p["wet_walls"]["tile_size_m"] == [0.6, 1.2] and warned(p, "assumed: tile size '60x120'", "cm", "no unit")
    p = prof("300x600 subway tiles")                                          # running bond: the long side is horizontal
    assert p["wet_walls"]["tile_size_m"] == [0.6, 0.3] and warned(p, "tile size '300x600'", "mm")
    p = prof("60x120 cm porcelain bathroom tiles")
    assert p["wet_walls"]["tile_size_m"] == [0.6, 1.2] and not warned(p, "tile size")
    own = prof("porcelain bathroom tiles")["wet_walls"]["tile_size_m"]       # the finish's own size
    p = prof("9000x9000 porcelain bathroom tiles")                            # no reading is a tile: listed, not used
    assert p["wet_walls"]["tile_size_m"] == own and warned(p, "tile size '9000x9000'", "not used")
    p = prof("6 x 12 m porcelain bathroom tiles")                             # an explicit unit is checked too
    assert p["wet_walls"]["tile_size_m"] == own and warned(p, "tile size '6 x 12 m'", "not used")


def test_review_low_an_unknown_plant_word_in_brackets_is_listed():
    p = prof("indoor plants (palms, orchids)")
    assert p["decor"]["plant_species"] == ["palm"] and warned(p, "'orchids'", "plants")
    p = prof("many indoor plants (palms, monstera; ferns)")
    assert p["decor"]["plant_species"] == ["palm", "monstera", "fern"] and not warned(p, "unknown plant")
    p = prof("large plants (fiddle leaf fig and 2 olive trees)")
    assert not warned(p, "unknown plant")


def test_the_lamps_claim_follows_the_lighting_table_of_record(monkeypatch):
    """Lead item (track E, #37): the profile says "the lamps are on" for exactly the moods whose
    ``finishes.LIGHTING[mood]["lamps_on"]`` is true, with or without a sun, and never for the others."""
    claim = lambda text: [w for w in prof(text)["warnings"] if "lamps are" in w]          # noqa: E731
    assert claim("interior evening") == ["interior evening mood: no sun, the lamps are on (table, floor, pendant and ceiling lights emit)"]
    assert claim("night") == ["night mood: no sun; interior lamps are off, renders will be dark"]
    assert claim("warm daylight") == []
    monkeypatch.setitem(FIN.LIGHTING, "warm daylight", {**FIN.LIGHTING["warm daylight"], "lamps_on": True})      # a mood with a sun
    assert claim("warm daylight") == ["warm daylight mood: the lamps are on (table, floor, pendant and ceiling lights emit)"]
    monkeypatch.setitem(FIN.LIGHTING, "night", {**FIN.LIGHTING["night"], "lamps_on": True})
    assert claim("night") == ["night mood: no sun, the lamps are on (table, floor, pendant and ceiling lights emit)"]
    monkeypatch.setitem(FIN.LIGHTING, "interior evening", {**FIN.LIGHTING["interior evening"], "lamps_on": False})
    assert claim("interior evening") == ["interior evening mood: no sun; interior lamps are off, renders will be dark"]
