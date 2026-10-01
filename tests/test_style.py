"""Style profile from the brief (wenart/style, Milestone 3 section 1): table, defaults, CLI."""
import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from wenart.style import profile as P
from wenart.style import vocabulary as V
from wenart.style.__main__ import main as style_main

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
FIXTURE = ROOT / "tests" / "fixtures" / "style_synthetic-01.json"

# brief text -> (floor slug, walls slug, lighting mood, unmatched phrases)
TABLE = [
    ("Scandinavian, light oak floor, white walls, linen textiles, warm daylight",
     "wood_oak_light", "plaster_white", "warm daylight", ["linen textiles"]),
    ("Modern minimal, polished concrete floor, charcoal and white, brass details, cool daylight",
     "concrete_polished", "plaster_charcoal", "cool daylight", ["brass details"]),
    ("Warm Mediterranean, terracotta floor, cream plaster walls, rattan and linen, golden evening light",
     "terracotta", "plaster_cream", "golden evening", ["rattan and linen"]),
    ("walnut floor, brick walls, overcast", "wood_walnut", "brick", "overcast", []),
    ("herringbone parquet, wood panelling, night", "wood_parquet", "wood_panel", "night", []),
    ("marble floor, white walls, cool daylight", "marble", "plaster_white", "cool daylight", []),
    ("carpet, cream walls, warm daylight", "carpet", "plaster_cream", "warm daylight", []),
    ("light tiles everywhere, white plaster, daylight", "tiles_light", "plaster_white", "warm daylight", []),
    # a floor phrase with a colour word must not recolour the walls
    ("white marble floor, brick, warm daylight", "marble", "brick", "warm daylight", []),
]


@pytest.mark.parametrize("text,floor,walls,mood,unmatched", TABLE)
def test_keyword_table(text, floor, walls, mood, unmatched):
    profile = P.profile_from_text(text)
    assert profile["floor"]["material"] == floor
    assert profile["walls"]["material"] == walls
    assert profile["lighting"]["mood"] == mood
    assert profile["lighting"]["hdri"] == V.LIGHTING[mood]["hdri"]
    assert profile["unmatched_terms"] == unmatched
    assert set(profile["matched_terms"]) | set(unmatched) == set(P.split_phrases(text))
    # every slug in the profile is a known material with an asset and a flat colour
    for slug in P.material_slugs(profile):
        assert slug in V.MATERIALS and slug in V.FLAT_COLOURS
    assert profile["floor"]["asset"] == V.MATERIALS[floor]["asset"]
    assert profile["walls"]["asset"] == V.MATERIALS[walls]["asset"]


def test_profile_shape_and_order():
    profile = P.profile_from_text("Scandinavian, warm daylight")
    assert tuple(profile.keys()) == P.PROFILE_KEYS
    assert set(profile["lighting"]) == {"hdri", "sun_elevation_deg", "sun_azimuth_deg", "sun_strength",
                                        "colour_temperature_k", "mood"}
    assert set(profile["walls"]) == {"material", "asset", "tint"} and len(profile["walls"]["tint"]) == 3
    assert set(profile["floor"]) == {"material", "asset"}
    assert set(profile["wet_floor"]) == {"material", "asset"}
    for slot in ("ceiling", "wet_walls", "trim", "door", "window_frame"):
        assert set(profile[slot]) == {"material"}


def test_family_fills_are_recorded_as_assumed():
    profile = P.profile_from_text("Scandinavian, warm daylight")
    assert profile["floor"]["material"] == "wood_oak_light"
    assert profile["walls"]["material"] == "plaster_white"
    assumed = [w for w in profile["warnings"] if w.startswith("assumed:")]
    assert len(assumed) == 2 and all("Scandinavian" in w or "scandinavian" in w for w in assumed)


def test_no_words_at_all_uses_defaults_and_says_so():
    profile = P.profile_from_text("something nobody understands")
    assert profile["unmatched_terms"] == ["something nobody understands"]
    assert profile["matched_terms"] == []
    assumed = [w for w in profile["warnings"] if w.startswith("assumed:")]
    assert len(assumed) == 3 and all("defaults.yaml" in w for w in assumed)
    defaults = P.load_defaults()["style"]["fallback"]
    assert profile["floor"]["material"] == defaults["floor"]
    assert profile["walls"]["material"] == defaults["walls"]
    assert profile["lighting"]["mood"] == defaults["light"]


def test_second_floor_word_is_ignored_and_noted():
    profile = P.profile_from_text("oak floor, marble, warm daylight")
    assert profile["floor"]["material"] == "wood_oak_light"
    assert any("ignored floor 'marble'" in w for w in profile["warnings"])
    profile = P.profile_from_text("charcoal and white, warm daylight")
    assert profile["walls"]["material"] == "plaster_charcoal"
    assert any("ignored wall word 'white'" in w for w in profile["warnings"])
    # a word inside the winning keyword is not reported as ignored
    profile = P.profile_from_text("cream plaster walls")
    assert not any("ignored" in w for w in profile["warnings"])


def test_derived_slots():
    wood = P.profile_from_text("oak floor")
    assert wood["door"]["material"] == "wood_oak_light"
    assert wood["wet_floor"]["material"] == "tiles_light"
    hard = P.profile_from_text("marble floor")
    assert hard["door"]["material"] == V.TRIM_MATERIAL
    assert hard["wet_floor"]["material"] == "marble"  # hard floors stay in wet rooms
    for profile in (wood, hard):
        assert profile["wet_walls"]["material"] == "tiles_light"
        assert profile["trim"]["material"] == "painted_wood_white"
        assert profile["window_frame"]["material"] == "painted_metal_white"
        assert profile["ceiling"]["material"] == "plaster_white"


def test_night_has_no_sun_and_warns():
    profile = P.profile_from_text("night")
    assert profile["lighting"]["sun_strength"] == 0
    assert any("night" in w for w in profile["warnings"])


def test_defaults_yaml_matches_the_code():
    """The default profile stored in wenart/defaults.yaml is what the code produces from the default text."""
    defaults = P.load_defaults()
    produced = P.profile_from_text(defaults["style"]["text"], defaults)
    assert produced == defaults["style"]["profile"]
    assert P.profiles_from_brief(None)[0]["floor"] == produced["floor"]
    assert P.profiles_from_brief(None)[0]["warnings"][0].startswith("assumed: no style in the brief")
    assert P.profiles_from_brief({})[0]["source_text"] == defaults["style"]["text"]


def test_multiple_styles():
    brief = yaml.safe_load((PROJECTS / "synthetic-03" / "brief.yaml").read_text(encoding="utf-8"))
    profiles = P.profiles_from_brief(brief)
    assert len(profiles) == 2
    assert [p["floor"]["material"] for p in profiles] == ["concrete_polished", "terracotta"]
    assert P.profile_from_brief(brief) == profiles[0]
    # style + styles: style first
    both = P.profiles_from_brief({"style": "oak floor", "styles": ["marble floor"]})
    assert [p["floor"]["material"] for p in both] == ["wood_oak_light", "marble"]


def test_wet_room_helpers():
    profile = P.profile_from_text("oak floor, white walls, warm daylight")
    assert P.is_wet_room("bathroom") and P.is_wet_room("wc") and P.is_wet_room("kitchen")
    assert not P.is_wet_room("living") and not P.is_wet_room(None)
    assert P.room_surfaces(profile, "bathroom") == {"floor": "tiles_light", "walls": "tiles_light",
                                                     "ceiling": "plaster_white", "wet": True}
    assert P.room_surfaces(profile, "bedroom") == {"floor": "wood_oak_light", "walls": "plaster_white",
                                                    "ceiling": "plaster_white", "wet": False}
    assets = P.assets_in_profile(profile)
    ids = [a for _, a, _ in assets["textures"]]
    assert len(ids) == len(set(ids)) and "WoodFloor051" in ids and "white_plaster_02" in ids
    assert assets["hdris"] == [("polyhaven", "kloppenheim_06")]


def test_vocabulary_tables_are_consistent():
    for keyword, slug in V.FLOOR_WORDS + V.WALL_WORDS:
        assert slug in V.MATERIALS, (keyword, slug)
        assert keyword == keyword.lower().strip()
    for keyword, mood in V.LIGHT_WORDS:
        assert mood in V.LIGHTING
    for family, table in V.STYLE_FAMILIES:
        assert set(table) == {"floor", "walls", "light"}
        assert table["floor"] in V.MATERIALS and table["walls"] in V.MATERIALS and table["light"] in V.LIGHTING
    for slug, entry in V.MATERIALS.items():
        assert entry["source"] in ("polyhaven", "ambientcg")
        assert len(entry["flat"]) == 3 and all(0.0 <= c <= 1.0 for c in entry["flat"])
    for slug in V.WALL_TINTS:
        assert slug in V.MATERIALS


def test_cli_on_synthetic_projects(tmp_path):
    for name, count in (("synthetic-01", 1), ("synthetic-02", 1), ("synthetic-03", 2)):
        out = tmp_path / name / "style.json"
        assert style_main([str(PROJECTS / name), "--out", str(out)]) == 0
        assert out.is_file()
        assert (out.with_name("style_2.json")).is_file() == (count == 2)
        profile = json.loads(out.read_text(encoding="utf-8"))
        assert tuple(profile.keys()) == P.PROFILE_KEYS
    # from a building.json (brief copied by the ingest pipeline into project.brief)
    out = tmp_path / "from_building.json"
    assert style_main([str(PROJECTS / "synthetic-01" / "truth" / "building.json"), "--out", str(out)]) == 0
    assert json.loads(out.read_text(encoding="utf-8")) == json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_is_current():
    """tests/fixtures/style_synthetic-01.json is what the CLI writes for projects/synthetic-01."""
    brief = yaml.safe_load((PROJECTS / "synthetic-01" / "brief.yaml").read_text(encoding="utf-8"))
    assert P.profile_from_brief(brief) == json.loads(FIXTURE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# No PyYAML (Blender's Python): the vocabulary and the default profile still work
# --------------------------------------------------------------------------

NO_YAML = ("import sys, json; sys.modules['yaml'] = None\n"            # 'import yaml' now raises ImportError
           "import wenart.style.vocabulary, wenart.style.__main__\n"
           "from wenart.style import default_profile\n"
           "print(json.dumps(default_profile()))\n")


def test_default_profile_without_yaml():
    """build.py runs inside Blender, whose Python has no PyYAML: the style package must import
    and give the default profile (through the vocabulary) all the same."""
    proc = subprocess.run([sys.executable, "-c", NO_YAML], capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    assert proc.returncode == 0, proc.stderr[-2000:]
    assert json.loads(proc.stdout) == P.load_defaults()["style"]["profile"]


def test_builtin_defaults_match_defaults_yaml():
    """The copy of the default text and slot fallbacks the code carries for Blender equals wenart/defaults.yaml."""
    defaults = P.load_defaults()
    assert P.BUILTIN_DEFAULTS["style"]["text"] == defaults["style"]["text"]
    assert P.BUILTIN_DEFAULTS["style"]["fallback"] == defaults["style"]["fallback"]
    assert P.default_profile() == defaults["style"]["profile"]
    assert P.default_profile()["walls"]["asset"] == V.MATERIALS["plaster_white"]["asset"]
