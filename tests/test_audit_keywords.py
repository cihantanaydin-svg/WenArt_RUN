"""Milestone 12 track B: title words in any language (docs/milestone12.md §6.1 code checks, ``keywords.py``).

The cases are the wrong objects of the diagnosis (§1.6) and the real titles of the library (ABO listings in EN, IT,
FR, ES, NL, SV; Sketchfab titles), plus Turkish, German and Dutch compounds of our projects."""
import pytest

from wenart.assets.audit import keywords as K


def test_fold_strips_accents_turkish_and_german_letters_and_splits_camel_case():
    assert K.fold("Çift Kişilik YATAK") == "cift kisilik yatak"
    assert K.fold("Bücherregal Straße") == "bucherregal strasse"
    assert K.fold("JuiceMachine") == "juice machine"
    assert K.fold("CandleHolder_skyrim") == "candle holder skyrim"
    assert K.tokens("Bed - Sample, 195x100cm") == ["bed", "sample", "195", "x", "100", "cm"]


@pytest.mark.parametrize("title,ftype,verdict", [
    ("Amazon Brand - Movian Aveyron Single Bed Frame, 195 x 100 x 80cm", "bed_single", "match"),
    ("Marchio Amazon - Movian Ackan - Divano a 3 posti", "sofa", "match"),
    ("Amazon Brand – Rivet Huxley Mid-Century Modern Accent Chair", "armchair", "match"),
    ("Amazon Brand – Rivet Federal Mid-Century Modern Wood Dining Room Kitchen Chairs", "chair", "match"),
    ("Amazon Brand – Stone & Beam Newport Nightstand End Table", "nightstand", "match"),
    ("Amazon Brand - Movian High Gloss 2 Drawer Bedside Cabinet", "nightstand", "match"),
    ("Amazon Brand – Stone & Beam Modern Bedroom Table Desk Lamp With Light Bulb", "table_lamp", "match"),
    ("Amazon Brand – Rivet Modern Mosaic Throw Pillow - 20 x 20 Inch, Blue", "cushion", "match"),
    ("Yemek Masası", "table_dining", "match"),
    ("Çift kişilik yatak", "bed_double", "match"),
    ("Kleiderschrank Eiche", "wardrobe", "match"),
    ("Boekenkast wit", "bookshelf", "match"),
    ("R RETRO FIRIN", "stove", "match"),
    ("Toilettes", "toilet", "match"),
    ("雙層床架", "bunk_bed", "match"),
    ("Movian Idro Skoskåp Ek", "tall_cabinet", "near"),
    ("Amazon Brand - Movian Corona Sideboard, 1 Door 4 Drawer", "dresser", "near"),
    ("MESA COMEDOR", "table_coffee", "conflict"),
    ("Marchio Amazon - Movian, armadio a 2 ante modello Mira", "tall_cabinet", "conflict"),
    ("Marque Amazon - Movian - Armoire 3 portes avec miroir Mira", "tall_cabinet", "conflict"),
    ("Grandfather Clock", "clock", "conflict"),
    ("Copper wall sconce", "pendant_light", "conflict"),
    ("Bathroom", "washbasin", "conflict"),
    ("Movian Indre Bedroom Furniture", "tall_cabinet", "silent"),
    ("Lpuvw", "armchair", "silent"),
    ("Rattan Tray", "basket", "conflict"),
    ("Светильник DL303-L7W Maytoni", "tray", "conflict"),
])
def test_title_verdicts(title, ftype, verdict):
    assert K.title_check(title, ftype)["verdict"] == verdict


def test_generated_titles_say_nothing():
    assert K.title_check("Generated classic bed single (1)", "bed_single", "generated")["verdict"] == "generated"


@pytest.mark.parametrize("title,category,word", [
    ("Intex Premaire Luchtbed met Fiber Tech-technologie", "wrong", "luchtbed"),
    ("Corpse", "wrong", "corpse"),
    ("Street Lamp", "outdoor", "street lamp"),
    ("Lamppost", "outdoor", "lamppost"),
    ("Simple Park Bench", "outdoor", "park bench"),
    ("Dedicated Bench, Museum Gardens, E2. (Raw Scan)", "outdoor", "gardens"),
    ("Lowpoly Bed", "crude", "lowpoly"),
    ("FF Desk Drawer 3D Test 5 Obj", "crude", "test"),
    ("Stylized Fridge", "crude", "stylized"),
    ("Amazon Brand – Stone & Beam Bagley Sectional Component, Armless Loveseat", "part", "sectional component"),
    ("Dining Set", "scene", "dining set"),
    ("A table, chairs & few cups", "scene", "table chairs"),
])
def test_flags(title, category, word):
    assert word in K.flags(title).get(category, [])


@pytest.mark.parametrize("title", [
    "Amazon Brand – Rivet King Street Industrial TV Media Console Table with Three Drawers",
    "Amazon Brand – Rivet Westline Modern Indoor Outdoor Hand-Painted Stoneware Flower Vase",
    "Amazon Brand – Ravenna Home Damask-Pattern Ceramic Garden Stool or Side Table, 16\"H, Grey",
    "Amazon Brand – Ravenna Home Parker Coffee Table, 47.2\"W, Marble & Gold",
    "nuLOOM Leaflet Fountain Boho Wool Area Rug, 7' 6\" x 9' 6\", Pink",
    "Amazon Brand – Stone & Beam Modern Print Wall Art of Brooklyn Bridge Sketch",
    "Amazon Brand – Stone & Beam Abstract Landscape Print on Canvas",
])
def test_real_indoor_products_carry_no_flag(title):
    assert K.flags(title) == {}


def test_the_longest_keyword_wins():
    assert K.named_families("Coffee Table")[0]["family"] == "table_coffee"
    assert [f["family"] for f in K.named_families("Decorative Throw Pillow")] == ["cushion"]
    assert K.named_families("Kitchen Bar Stool")[-1]["family"] == "bar_stool"


def test_a_room_word_next_to_a_piece_is_ignored():
    chk = K.title_check("Modern Living Room Chair", "armchair")
    assert chk["verdict"] == "match" and "room" not in chk["families"]


def test_the_suggested_type_of_a_conflicting_title():
    chk = K.title_check("Marchio Amazon - Movian, armadio a 2 ante modello Mira", "tall_cabinet")
    assert K.suggested_type(chk, "furniture", {"wardrobe", "tall_cabinet"}) == "wardrobe"
    chk = K.title_check("Bathroom", "washbasin")
    assert K.suggested_type(chk, "furniture", {"washbasin"}) is None
