"""CPU tests of the ABO rules for the 14 new furniture and 12 new decor types (docs/milestone10.md §4.5, §4.6).

Every row below is a real listing of the ABO metadata read on 8 Oct 2026 (product type, English item name, the model's
box in the importer's Z-up frame: x, z, y of the csv), so a rule change that breaks a mapping shows here. The counts
per type of that session are in ``results/library/survey_m10_session.json``; this file checks the committed numbers are
current (``abo.yaml`` and ``objaverse.yaml`` unchanged since they were counted) and have the right shape.
"""
import json
from pathlib import Path

import pytest

from wenart.assets import abo as A
from wenart.assets import objaverse as OV

ROOT = Path(__file__).resolve().parents[1]
SESSION = ROOT / "results" / "library" / "survey_m10_session.json"
CFG = A.load_config()
OCFG = OV.load_config()
NEW_FURNITURE = ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
                 "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
NEW_DECOR = ("curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture", "plant_large",
             "pendant_light", "ceiling_light")
# Types the 8 Oct 2026 listings hold no model of: no ABO rule (Objaverse and the generated models fill them).
NO_ABO_LISTING = ("crib", "curtain", "blind", "throw", "books")


def mapped(ptype, name, dims):
    rule = A.match_rule(ptype, name, dims[2], CFG["rules"])
    if rule is None:
        return None
    table, tol = OV.library_size_table(OCFG)
    return A.resolve_type(rule, dims, OCFG, table, tol)[0]


@pytest.mark.parametrize("ptype, name, dims, expect", [
    # bunk beds: only "bunk" names; a loft bed is not one
    ("BED", "Max & Finn Twin Floor Bunk Bed, Gray", [2.013, 1.1054, 1.2061], "bunk_bed"),
    ("BED", "AmazonBasics Metal Twin Loft Bed, Easy Assembly, Black", [1.39, 1.97, 1.29], None),
    # corner sofas: sectionals and sofa chaises; modules, outdoor sets and armchairs are not
    ("SOFA", 'Amazon Brand – Rivet Emerly Modern Sectional Sofa, 96"W, Ecru', [2.4481, 2.4301, 0.867], "sofa_corner"),
    ("SOFA", 'Amazon Brand – Rivet Emerly Modern Sofa Chaise, 96"W, Pewter', [2.44, 1.62, 0.99], "sofa_corner"),
    ("SOFA", "Rivet Revolve Upholstered Sofa", [1.98, 0.94, 0.92], "sofa"),
    ("SOFA", "AmazonBasics Aluminum Outdoor L-Shaped Sofa Lounge Set with Cushions and Table - Grey",
     [2.10, 1.66, 0.76], None),
    ("CHAIR", 'Amazon Brand – Stone & Beam Bagley Sectional Component, Wedge, Fabric, 67"W, Linen',
     [1.05, 1.0424, 0.9371], None),
    ("CHAIR", "amazon Brand Movian City Club Module Corner Armchair", [0.684, 0.6849, 0.66], "armchair"),
    # chaise longues
    ("CHAIR", 'Amazon Brand – Ravenna Home Classic Tufted Chaise Lounge, 58.3" Length, Slate Grey',
     [0.6752, 1.3795, 0.7868], "chaise"),
    ("CHAIR", 'Amazon Brand – Stone & Beam Varon Modern Lounge Daybed Chaise, 34.2"W, Dark Grey',
     [0.8943, 1.7793, 0.8589], "chaise"),
    ("CHAIR", "AmazonBasics Outdoor Zero Gravity Lounge Folding Chair, Black", [0.70, 0.88, 1.16], None),
    # office chairs
    ("CHAIR", "AmazonBasics Mesh, Mid-Back, Adjustable, Swivel Office Desk Chair with Armrests, Black",
     [0.6101, 0.6402, 1.0259], "office_chair"),
    ("CHAIR", "AmazonBasics High-Back Executive Chair - Black", [0.7, 0.78, 1.15], "office_chair"),
    ("HOME_FURNITURE_AND_DECOR", 'AmazonBasics 55" L-Shape Office Corner Desk - Espresso', [1.40, 1.40, 0.76], None),
    # bar stools
    ("STOOL_SEATING", 'Amazon Brand – Stone & Beam Sophia Modern Swivel Kitchen Bar Stool, 43.3"H, Slate Grey',
     [0.4772, 0.5697, 1.11], "bar_stool"),
    ("CHAIR", 'Amazon Brand – Stone & Beam Classic Tufted Counter-Height Barstool, Set of 2, 37"H, Beige',
     [0.5241, 0.626, 0.9376], "bar_stool"),
    ("STOOL_SEATING", "AmazonBasics Multi-Purpose Drafting Spa Bar Stool with Wheels - Black", [0.67, 0.64, 0.58],
     None),
    ("STOOL_SEATING", 'Rivet Stevie Mid-Century Modern Bar Stool, 30"H, Pack of 2, Blue', [0.46, 0.46, 0.52], None),
    # benches, ottomans
    ("BENCH", 'Amazon Brand – Rivet Martin Modern Storage Bench, 39"W, Sundried Velvet', [1.0159, 0.4918, 0.4708],
     "bench"),
    ("BENCH", "AmazonBasics Standard Adjustable Padded Piano and Keyboard X-Style Bench", [0.42, 0.32, 0.50], None),
    ("FITNESS_BENCH", "AmazonBasics Flat Weight Workout Exercise Bench - 41 x 20 x 11 Inches, Black",
     [0.44, 1.07, 0.45], None),
    ("OTTOMAN", 'Amazon Brand – Rivet Ava Mid-Century Modern Upholstered Ottoman Bench, 63.4"W, Dark Grey',
     [1.5979, 0.6309, 0.384], "bench"),
    ("OTTOMAN", 'Amazon Brand – Rivet Sloane Mid-Century Modern Ottoman with Tapered Legs, 32"W, Charcoal',
     [0.8232, 0.6104, 0.4782], "ottoman"),
    ("HOME_FURNITURE_AND_DECOR", "Amazon Brand - Rivet Ross Tweed Lift-Top Storage Ottoman/Footstool with inner "
                                 "tray, 45 x 45 x 46cm, Navy Blue", [0.45, 0.45, 0.46], "ottoman"),     # not a tray
    ("CHAIR", 'Amazon Brand – Rivet Lawson Modern Angled Ottoman, 27"W, Charcoal', [0.69, 0.51, 0.41], "ottoman"),
    # console tables (a TV console is a TV unit, a bar-height one is neither)
    ("TABLE", "Amazon Brand - Movian Corona Console Table, 2 Drawer With Shelf, Solid Pine Wood, 70 x 83 x 31 cm",
     [0.8999, 0.3399, 0.728], "console_table"),
    ("DESK", "AmazonBasics Retro Hairpin Console Table - Espresso with Black Legs", [0.9906, 0.4986, 0.6604],
     "console_table"),
    ("TABLE", "Amazon Brand – Rivet Industrial Metal Leg TV Media Console, Walnut", [1.8, 0.47, 0.42], "tv_unit"),
    ("TABLE", 'Amazon Brand – Rivet Hairpin Wood and Metal Tall 29.5" Console Bar Table, Walnut and Black',
     [1.57, 0.43, 0.83], None),
    # cabinets
    ("CABINET", "Amazon Brand - Movian Corona Sideboard, 3 Door 3 Drawer, Solid Pine Wood ,Waxed,", [1.3208, 0.4318,
                                                                                                    0.8103],
     "sideboard"),
    ("CABINET", "Amazon Brand - Movian Loue 2-Door 4-Drawer Sideboard Storage Cabinet, 145 x 90 x 38cm",
     [1.4498, 0.38, 0.8999], "sideboard"),
    ("CABINET", "Amazon Brand - Movian Indre 1-Door Shoe Cabinet/Cupboard/Organizer with Mirror, 23 x 50 x 179cm, "
                "Light Brown Oak-Effect", [0.50, 0.23, 1.79], "shoe_cabinet"),
    ("CLOTHES_RACK", "AmazonBasics Easy Assemble Shoe Rack - 4-Tier, Silver", [1.17, 0.23, 0.67], "shoe_cabinet"),
    ("BENCH", "AmazonBasics Classic Shoe Bench with Lift-Top Compartment and 3 Storage Cubbies - Black Oak",
     [0.91, 0.40, 0.50], "shoe_cabinet"),                                  # the shoe rule comes before the bench rule
    ("CABINET", "Amazon Brand - Alkove Malvern Solid Wood Front Display Cabinet, 66 x 198 x 42cm, Dark Brown/Black",
     [0.66, 0.42, 1.98], "display_cabinet"),
    ("HOME", "AmazonBasics Flag Display Case, White", [0.64, 0.10, 0.34], None),
    ("CABINET", "Amazon Brand – Stone & Beam Farmhouse Wall Mounted Cabinet Storage Organzier - 23 x19 x 6 Inch, "
                "Natural Wood", [0.489, 0.1838, 0.5903], "wall_cabinet"),
    ("CABINET", "Amazon Brand - Movian Argenton - Wall-mounted Bathroom Cabinet, 2-Doors 4-Shelves, 30 x 27 x 140 cm",
     [0.30, 0.27, 1.40], None),                                            # taller than a wall cabinet: size refused
    ("CABINET", "Express Furniture", [1.2499, 0.4798, 2.1598], "tall_cabinet"),   # no rule words: height >= 1.4 m
    ("CABINET", "Express Möbel Cargo 2-Door Sliding Door Cabinet", [2.0, 0.68, 2.16], None),    # wider than a cabinet
    ("CABINET", "Corona Wardrobe, 3 Door", [1.5, 0.57, 1.87], "wardrobe"),
    # decor
    ("CANDLE_HOLDER", "Amazon Brand – Stone & Beam Rustic-Look Stoneware Decorative Candle Holder, 9.4 Inch Height, "
                      "White and Clay", [0.1096, 0.1096, 0.2389], "candle"),
    ("HOME", "Amazon Brand – Rivet Modern Cylindrical Stoneware Candle Holder Lantern Home Decor Set - Set of 2, "
             "Gray and Cream", [0.35, 0.18, 0.26], "candle"),
    ("CANDLE_HOLDER", "Amazon Brand – Stone & Beam Modern Coastal Raffia Ceiling Hanging Pendant Chandelier Fixture "
                      "With Built-In LED", [0.45, 0.45, 0.72], "pendant_light"),          # a light, not a candle
    ("HOME", "Amazon Brand – Rivet Modern Geometric Handwoven Round Basket Set - Set of 3, White / Black",
     [0.3514, 0.917, 0.3561], "basket"),
    ("BASKET", 'Rivet Modern Tall Geometric Wire Baskets, Set of 2, 13.25"H and 10.75"H, Silver', [0.81, 0.45, 0.34],
     "basket"),
    ("TABLE", 'Amazon Brand – Rivet Meeks Round Side Table with Fabric Storage Basket, 24"H, Walnut and Grey',
     [0.40, 0.40, 0.62], "side_table"),
    ("HOME", "Amazon Brand – Rivet Mid Century Modern Glam Serving Tray - 3.5 x 11 x 11 Inch, Gold and Blue",
     [0.4437, 0.3037, 0.0842], "tray"),
    ("TABLE", "AmazonBasics Classic TV Dinner Folding Trays with Storage Rack, Espresso - Set of 4",
     [0.48, 0.38, 0.66], None),
    ("CLOCK", 'Amazon Brand - Solimo 12" Wall Clock - Paramount Dark Paneling (Silent Movement, Black Frame)',
     [0.2932, 0.0403, 0.2932], "clock"),
    ("HOME", 'Amazon Brand – Rivet Modern Minamalist Wood-Face Clock, 12"H, Walnut', [0.31, 0.04, 0.31], "clock"),
    ("FIGURINE", "Amazon Brand – Rivet Mid Century Modern Polyresin Stag Head Figurine Home Decor - 12.5 Inch, White",
     [0.1745, 0.224, 0.3288], "sculpture"),
    ("SCULPTURE", 'Amazon Brand – Rivet Urban Mid-Century Modern Concrete Rectangle Planter Boxes, Set of 3, 5" x 3" '
                  'x 2", Blue', [0.4608, 0.0816, 0.0507], None),                          # a planter set, not a sculpture
    ("LIGHT_FIXTURE", 'Amazon Brand – Stone & Beam Industrial Farmhouse Indoor Pendant Ceiling Light with Bulb, '
                      'Adjustable 15"- 63" Cord', [0.341, 0.341, 0.8486], "pendant_light"),
    ("LIGHT_FIXTURE", "Amazon Brand – Rivet Modern Industrial Geometric Cage Pendant Chandelier Fixture With Light "
                      "Bulb - 10.5 x 10.5", [0.4871, 0.4313, 1.7642], "pendant_light"),
    ("LIGHT_FIXTURE", 'Amazon Brand – Ravenna Home Casual Flush Mount, 4"H, Brushed Nickel', [0.3546, 0.356, 0.1019],
     "ceiling_light"),
    ("LIGHT_FIXTURE", "Amazon Brand – Stone & Beam Schoolhouse Semi-Flush Mount Ceiling Fixture With Light Bulb",
     [0.2794, 0.2794, 0.2694], "ceiling_light"),
    ("LIGHT_FIXTURE", "Amazon Brand – Stone & Beam Modern Metal Wall Mount Sconce Fixture With Light Bulb And Glass "
                      "Shade - 16 x 8 x 10 Inch", [0.20, 0.25, 0.27], None),
    ("ELECTRIC_FAN", "Amazon Brand – Rivet Modern Angular 3 Blade Ceiling Flush Mount Fan with Integrated LED Light",
     [1.07, 1.07, 0.30], None),                                           # a ceiling fan is no light
    ("PLANTER", "Amazon Brand – Rivet Mid-Century Modern Stoneware Indoor Hanging Planter Flower Pot with Rope, 5\"H, "
                "Speckled White", [0.22, 0.22, 1.03], "plant"),          # hanging: no large plant
    ("CURTAIN", 'Amazon Brand – Stone & Beam Modern Impressionistic Floral Print Wall Art on Canvas, 36" x 24"',
     [0.91, 0.04, 0.60], None),                                           # the product type CURTAIN holds wall art
    ("BLANKET", "Amazon Brand – Rivet Contemporary Fir Decorative Blanket Ladder with Iron Rungs - 71.65\"H, Black",
     [0.44, 0.20, 1.81], None),                                           # a blanket ladder is no throw
])
def test_mapping_table_m10(ptype, name, dims, expect):
    assert mapped(ptype, name, dims) == expect


def test_the_new_rules_leave_the_old_types_alone():
    """Only 16 of the 7,953 listings changed their type against the M9 rules (4 Oct 2026 numbers): 7 bar stools
    typed CHAIR, 6 chaise sofas, 2 console tables typed DESK, 1 ergonomic chair. The first 24 ABO candidates of the
    other types stay the M8 ones."""
    first = {r["name"]: i for i, r in enumerate(CFG["rules"])}
    for old, new in (("bed", "bunk_bed"), ("sofa_corner", "sofa"), ("sofa_named", "chaise"), ("chaise", "armchair"),
                     ("office_chair", "armchair"), ("bar_stool", "chair"), ("ottoman_named", "armchair"),
                     ("tv_unit", "console_table"), ("console_table", "side_table"), ("dresser_named", "sideboard"),
                     ("shoe_cabinet", "bench"), ("bench", "ottoman"), ("vase_named", "candle_named"),
                     ("candle_named", "rug"), ("plant_large", "plant")):
        assert first[old] < first[new], (old, new)


def test_every_new_type_has_an_abo_rule_or_a_reason():
    ruled = {t for rule in CFG["rules"] for t in rule["types"]}
    for t in NEW_FURNITURE + NEW_DECOR:
        if t in NO_ABO_LISTING:
            assert t not in ruled, f"{t}: the 8 Oct 2026 listings hold no model: no rule (abo.yaml says so)"
        else:
            assert t in ruled, t
    assert set(CFG["no_listing"]) == set(NO_ABO_LISTING) and all(CFG["no_listing"].values())
    assert "wall-art canvases" in CFG["no_listing"]["curtain"] and "blanket ladder" in CFG["no_listing"]["throw"]
    table, _tol = OV.library_size_table(OCFG)
    for rule in CFG["rules"]:
        for t in rule["types"]:
            for real in (OV.BED_TYPES if t == "bed" else [t]):
                assert real in table and real in OV.heights_of(OCFG), (rule["name"], real)


def test_rules_use_the_product_types_of_the_listings_only():
    """Every product type a new rule names is a product type of the ABO listings (read 8 Oct 2026)."""
    seen = set(json.loads(SESSION.read_text(encoding="utf-8"))["listings"]["product_types"])
    names = {r["name"] for r in CFG["rules"]}
    old = {"bed", "sofa", "sofa_named", "armchair", "chair", "table_coffee", "nightstand", "tv_unit", "side_table",
           "table_dining", "desk", "desk_named", "wardrobe", "dresser", "dresser_named", "bookshelf",
           "bookshelf_named", "floor_lamp", "table_lamp", "vase", "vase_named", "mirror", "mirror_named", "rug",
           "rug_named", "wall_art", "wall_art_named", "cushion", "cushion_named", "plant", "plant_named"}
    for rule in CFG["rules"]:
        if rule["name"] in old:
            continue
        for ptype in rule["product_types"]:
            assert ptype in seen, f"{rule['name']}: {ptype} is no product type of the listings"
    assert len(names) == len(CFG["rules"])


# --------------------------------------------------------------------------
# The committed session survey
# --------------------------------------------------------------------------

def test_session_survey_numbers_are_committed_and_current():
    doc = json.loads(SESSION.read_text(encoding="utf-8"))
    assert doc["kind"] == "abo_session_survey" and doc["date"] == "2026-10-08"
    assert set(doc["config_sha256"]) == {"abo.yaml", "objaverse.yaml"}            # what the numbers were counted with
    assert doc["listings"]["models"] == 7953 and doc["listings"]["with_3d_model"] == 7960
    new = doc["new_types"]
    assert set(new) == set(NEW_FURNITURE) | set(NEW_DECOR)
    for t, row in new.items():
        assert set(row) >= {"kind", "mapped", "in_size_range", "candidates", "rules", "note"}, t
        assert row["candidates"] == min(row["in_size_range"], doc["per_type_limit"]), t
        assert row["in_size_range"] <= row["mapped"], t
        assert row["kind"] == ("decor" if t in NEW_DECOR else "furniture"), t
        assert row["in_size_range"] >= 20 or row["note"], f"{t}: a short type says why"
        if t in NO_ABO_LISTING:
            assert row["mapped"] == 0 and row["note"], t
    assert doc["old_types"]["sofa"]["in_size_range"] == 742       # M9: 748; six chaise sofas are corner sofas now
    for t in ("armchair", "chair", "sofa", "desk", "side_table", "table_coffee"):
        assert t in doc["old_types"]
    assert doc["candidates_total"] == sum(r["candidates"] for r in list(new.values()) + list(doc["old_types"].values()))
    assert all(len(f["sha256"]) == 64 for f in doc["metadata_files"].values())


def test_session_summary_from_a_survey(tmp_path):
    """``survey --summary FILE`` writes the counts per new type of the survey it just made (here the canned
    metadata of tests/fixtures/abo: one corner sofa and one office chair among 38 listings)."""
    fixture = Path(__file__).resolve().parent / "fixtures" / "abo"
    summary = tmp_path / "summary.json"
    assert A.main(["survey", "--metadata", str(fixture), "--no-download", "--out", str(tmp_path / "lib"),
                   "--summary", str(summary)]) == A.EXIT_OK
    doc = json.loads(summary.read_text(encoding="utf-8"))
    new = doc["new_types"]
    assert set(new) == set(NEW_FURNITURE) | set(NEW_DECOR)
    assert new["sofa_corner"]["mapped"] == 1 and new["sofa_corner"]["rules"] == {"sofa_corner": 1}
    assert new["office_chair"]["candidates"] == 1 and new["crib"]["mapped"] == 0 and "baby bed" in new["crib"]["note"]
    assert doc["old_types"]["sofa"]["rules"] == {"sofa": 1, "sofa_named": 1} and doc["listings"]["models"] == 37
    assert doc["listings"]["product_types"]["SOFA"] == 2 and doc["candidates_total"] == 31
    assert "sofa_corner" not in doc["old_types"] and "sofa" not in new
    assert A.new_types(CFG)[:2] == ["bunk_bed", "sofa_corner"]      # the first type of a since-m10 rule
