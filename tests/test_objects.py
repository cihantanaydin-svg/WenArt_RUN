"""Object word table and per-object word tables (wenart/style/objects.py, docs/milestone10.md §4.1)."""
import json
from pathlib import Path

import pytest

from wenart.style import colours as C
from wenart.style import finishes as F
from wenart.style import objects as O
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
BUILDING_SCHEMA = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))

SPEC_OBJECTS = ("walls", "accent_wall", "floor", "ceiling", "sofa", "armchair", "chair", "bed", "cushions", "throws", "curtains", "rug",
                "cabinets", "kitchen", "worktop", "furniture", "table_coffee", "table_dining", "doors", "handles", "window_frames",
                "pots", "plants", "facade", "roof", "paving", "garden", "lighting")


def test_find_spans_is_whole_word_earliest_then_longest_and_never_overlaps():
    table = [("oak", "a"), ("light oak", "b"), ("ash", "c"), ("plank", "d"), ("oak plank", "e")]
    spans = O.find_spans("light oak plank floor", table)
    assert [(s.keyword, s.value) for s in spans] == [("light oak", "b"), ("plank", "d")]          # earliest start, longest keyword
    assert O.find_spans("ashlar and ash", table)[0].keyword == "ash" and len(O.find_spans("ashlar and ash", table)) == 1   # whole words
    assert O.find_spans("oak", table, taken=[(0, 3)]) == []                                       # a claimed range is skipped
    assert O.first_span("no hit here", table) is None and O.first_span("oak", table).value == "a"
    assert O.find_spans("béton brut", [("béton brut", 1)])[0].value == 1                           # non-ASCII words


def test_object_table_holds_the_objects_of_the_spec():
    assert set(SPEC_OBJECTS) <= set(O.OBJECTS)
    assert {obj for _, obj in O.OBJECT_WORDS} <= set(O.OBJECTS)
    assert set(SPEC_OBJECTS) <= {obj for _, obj in O.OBJECT_WORDS}
    for word, obj in O.OBJECT_WORDS:
        assert word == word.lower().strip(), word
    seen = {}
    for word, obj in O.OBJECT_WORDS:
        assert seen.setdefault(word, obj) == obj, f"{word!r} names two objects"
    assert O.OBJECT_IN_KEYWORDS <= set(O.OBJECTS)


def test_furniture_objects_stand_for_schema_types():
    types = set(BUILDING_SCHEMA["$defs"]["furniture"]["properties"]["type"]["enum"])
    for obj, names in O.OBJECT_TYPES.items():
        assert obj in O.OBJECTS and set(names) <= types, obj
    assert set(O.UPHOLSTERED) <= set(O.OBJECT_TYPES)
    assert O.OBJECT_TYPES["sofa"] == ("sofa", "sofa_corner")


def test_the_word_tables_name_known_slugs_and_values():
    for table in (O.FRAME_WORDS, O.DOOR_WOOD_WORDS, O.WET_WALL_WORDS, *O.EXTERIOR_WORDS.values()):
        for word, slug in table:
            assert slug in V.MATERIALS, (word, slug)
    assert {v for _, v in O.CABINET_FRONT_WORDS} == set(F.CABINET_FRONT_STYLES)
    assert {v for _, v in O.WORKTOP_WORDS} == set(F.CABINET_WORKTOPS)
    assert {v for _, v in O.HANDLE_WORDS} == set(F.CABINET_HANDLES)
    assert {v for _, v in O.DOOR_STYLE_WORDS} == set(F.DOOR_STYLES)
    species = set(BUILDING_SCHEMA["$defs"]["decor"]["properties"]["species"]["enum"]) - {None}
    assert {v for _, v in O.PLANT_WORDS} <= species and set(F.PLANT_SPECIES) == species
    assert set(O.POT_MATERIAL_WORDS and {v for _, v in O.POT_MATERIAL_WORDS}) <= set(F.POT_MATERIALS)
    for word, mat in F.POT_MATERIALS.items():
        assert mat in V.MATERIALS or mat in V.FURNITURE_MATERIALS, word
    tags = set(BUILDING_SCHEMA["$defs"]["furniture"]["properties"]["design"]["properties"]["material_tags"]["items"]["enum"])
    assert {v for _, v in O.MATERIAL_TAG_WORDS} <= tags
    assert set(O.EXTERIOR_WORDS) <= set(F.EXTERIOR_SLOTS) and set(O.OBJECT_EXTERIOR_SLOT.values()) <= set(O.EXTERIOR_WORDS)
    for slot, words in O.EXTERIOR_WORDS.items():
        for _, slug in words:
            assert slug in F.EXTERIOR_MATERIALS[slot], (slot, slug)


def test_wood_slug_reads_type_and_tone():
    cases = {("natural", "light", "wood"): "wood_veneer_oak_light", ("oak",): "wood_veneer_oak", ("light", "oak"): "wood_veneer_oak_light",
             ("dark", "oak"): "wood_veneer_black_oak", ("smoked", "oak"): "wood_veneer_black_oak", ("walnut",): "wood_veneer_walnut",
             ("dark", "wood"): "wood_veneer_walnut", ("wood",): "wood_veneer_oak", ("pale", "wooden"): "wood_veneer_oak_light",
             ("ash",): "wood_veneer_ash", ("birch",): "wood_veneer_maple", ("teak",): "wood_veneer_teak", ("cherry",): "wood_veneer_cherry"}
    for words, slug in cases.items():
        assert O.wood_slug(words) == slug, words
        assert slug in V.FURNITURE_MATERIALS
    assert O.wood_slug(("light", "grey")) is None and O.wood_slug(()) is None


def test_tile_sizes():
    assert O.tile_sizes("60x120 cm tiles")[0][0] == [0.6, 1.2]
    assert O.tile_sizes("7.5 x 15 cm subway")[0][0] == [0.075, 0.15]
    assert O.tile_sizes("10 by 10 cm zellige")[0][0] == [0.1, 0.1]
    assert O.tile_sizes("30 x 60 mm mosaic")[0][0] == [0.03, 0.06]
    assert O.tile_sizes("2,5x2,5 mosaic")[0][0] == [0.025, 0.025]
    assert O.tile_sizes("1.2 x 0.6 m slab")[0][0] == [1.2, 0.6]
    assert O.tile_sizes("no size here") == []
    text = "a 60x120 cm tile"
    (size, (a, b)), = O.tile_sizes(text)
    assert text[a:b] == "60x120 cm"


def test_descriptors_modifiers_and_amounts_do_not_overlap_with_colours_or_objects():
    assert not (O.DESCRIPTORS & set(C.NAMES)) and not (O.MODIFIER_WORDS & O.DESCRIPTORS)
    assert O.MODIFIER_WORDS == set(C.MODIFIERS)
    assert not ({w for w, _ in O.OBJECT_WORDS} & O.DESCRIPTORS)
    assert set(O.AMOUNT_WORDS.values()) == {"many", "some", "few"}
    assert O.ACCENT_ROOM_TYPES == ("living", "bedroom") and "behind the sofa or the bed head" in O.ACCENT_RULE
    assert O.STYLE_TAGS["natural"]["furniture_wood"] in V.FURNITURE_MATERIALS


def test_track_e_exterior_words_are_covered():
    """wenart/blender/exterior.py keeps a temporary word table (``EXTERIOR_WORDS``, material names of its own): every word it knows
    for facade, roof, paving and garden is known here and gives the same slug, window-frame and door words give the slug
    that replaces E's short name (see ``E_NAMES``)."""
    ext = pytest.importorskip("wenart.blender.exterior")
    table = getattr(ext, "EXTERIOR_WORDS", None)
    if not table:
        pytest.skip("track E removed its temporary table")
    from wenart.style import profile as P

    E_NAMES = {"pvc": "pvc_white", "aluminium": "aluminium_anthracite", "steel": "steel_black", "stone": "paving_stone"}
    STEMS = {"alumin": "aluminium"}                                              # E matches word stems, the tables whole words
    for slot, words in table.items():
        for word, e_slug in words:
            if slot == "door" and e_slug == "glass":
                continue                                                          # a glazed door is a door style, not a material
            found, _ = P.exterior_look_from_words(slot, STEMS.get(word, word))
            assert found and found["material"], f"E knows '{word}' for {slot}, the style tables do not"
            want = E_NAMES.get(e_slug, e_slug)
            assert found["material"] == want, (slot, word, found["material"], want)
