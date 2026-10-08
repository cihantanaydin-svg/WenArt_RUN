"""The walls' paint colour and the accent wall in the polish prompt and in the gate's albedo record (Milestone 10,
docs/milestone10.md §4.1; the style profile of track C: ``walls.colour``, ``wall_accent``, lighting moods with
``lamps_on``).

What: ``wenart.polish.prompt`` says "warm greige painted walls" (through its own ``surface_words``, not another
track's word tables), names the accent wall only in the room types the profile lists, takes the wet-wall tile
colour in wet rooms and says the light comes from the lamps for a lamps-on mood; ``wenart.gate.colour`` records the
expected wall colour (CIELAB, chroma), treats a paint colour as a flat colour and makes the walls region ``texture``
in a room that has a textured accent wall.

Why: a paint colour that is neither in the prompt nor in the gate's record is silently lost between the brief
and the polished image.

How: profiles and scene manifests as plain dicts; ``wenart.style.colours`` is replaced by a stand-in with
``linear_rgb`` / ``canonical_phrase`` where the real table is not filled yet.
"""
import types

import pytest

from wenart.gate import colour as GC
from wenart.polish import prompt as PR

GREIGE = (0.48, 0.42, 0.35)           # linear RGB of the stand-in colour table


@pytest.fixture
def colours(monkeypatch):
    """A stand-in for ``wenart.style.colours`` (track C's table) that knows two phrases."""
    table = {"warm greige": GREIGE, "greige": (0.45, 0.40, 0.34), "terracotta": (0.45, 0.17, 0.09)}

    def linear_rgb(phrase, modifiers=()):
        return table[str(phrase).lower()]

    def canonical_phrase(text):
        return str(text).lower() if str(text).lower() in table else None

    import wenart.style as pkg
    stand_in = types.SimpleNamespace(NAMES=tuple(table), linear_rgb=linear_rgb, canonical_phrase=canonical_phrase)
    monkeypatch.setitem(__import__("sys").modules, "wenart.style.colours", stand_in)
    monkeypatch.setattr(pkg, "colours", stand_in, raising=False)
    return stand_in


def profile(**changes) -> dict:
    base = {"family": "modern", "floor": {"material": "wood_oak_light", "asset": None, "colour": None},
            "walls": {"material": "paint", "asset": None, "colour": "warm greige"},
            "wall_accent": None, "wet_walls": {"material": "tiles_light", "asset": None, "colour": "sage"},
            "lighting": {"mood": "warm daylight"}}
    base.update(changes)
    return base


# --------------------------------------------------------------------------
# The polish prompt
# --------------------------------------------------------------------------

def test_the_wall_colour_is_in_the_prompt_in_front_of_the_finish(colours):
    out = PR.build_prompt(profile(), "living", ["sofa"], 18.0)
    assert out["walls_colour"] == "warm greige" and out["warnings"] == [], out["warnings"]
    # Track C's words for `paint` ("smooth painted") follow the colour.
    assert f"Warm greige {PR.MATERIAL_WORDS['paint']} walls, light oak wood floor, sofa." in out["prompt"]
    # A colour phrase the table knows only as an alias is said in its canonical form; an unknown one as written.
    assert PR.colour_phrase("Warm Greige") == "warm greige" and PR.colour_phrase("Dusty_Mauve") == "dusty mauve"
    assert PR.colour_phrase(None) is None and PR.colour_phrase("  ") is None


def test_without_a_colour_the_prompt_is_the_old_one():
    out = PR.build_prompt(profile(walls={"material": "plaster_white", "asset": None, "colour": None}), "living", [])
    assert "White plaster walls, light oak wood floor." in out["prompt"] and out["walls_colour"] is None
    assert PR.surface_words("plaster_white", None, "wall material", []) == "white plaster"
    # A colour already inside the material words is not said twice.
    assert PR.surface_words("plaster_cream", "cream", "wall material", []) == "cream plaster"


def test_a_wet_room_takes_the_colour_of_its_wet_wall_slot(colours):
    out = PR.build_prompt(profile(), "bathroom", ["toilet"])
    assert out["walls"] == "tiles_light" and out["walls_colour"] == "sage"
    assert "Sage light ceramic tile walls" in out["prompt"]
    # No wet-wall slot: the room's walls (and their colour) are used, as the scene builder does.
    out = PR.build_prompt(profile(wet_walls=None), "bathroom", [])
    assert out["walls"] == "paint" and out["walls_colour"] == "warm greige"


def test_the_accent_wall_is_named_only_in_the_room_types_the_profile_lists(colours):
    accent = {"material": "paint", "asset": None, "colour": "terracotta", "room_types": ["living", "bedroom"],
              "rule": "the wall behind the sofa"}
    living = PR.build_prompt(profile(wall_accent=accent), "living", ["sofa"])
    assert f"one terracotta {PR.MATERIAL_WORDS['paint']} accent wall" in living["prompt"] and living["accent"]
    assert living["prompt"].index("painted walls") < living["prompt"].index("accent wall") < \
        living["prompt"].index("floor")
    hall = PR.build_prompt(profile(wall_accent=accent), "hall", [])
    assert "accent" not in hall["prompt"] and hall["accent"] is None
    assert PR.accent_words(profile(wall_accent={"material": None, "room_types": ["living"]}), "living", []) is None


def test_a_material_with_no_words_is_listed_not_guessed():
    warnings: list = []
    assert PR.surface_words("glitter_wall", "sage", "wall material", warnings) == "sage glitter wall"
    assert warnings == ["no prompt words for wall material 'glitter_wall'; used the slug"]
    assert PR.surface_words(None, "sage", "wall material", []) == "sage"


def test_a_lamps_on_mood_says_the_light_comes_from_the_lamps(monkeypatch):
    monkeypatch.setitem(PR.VOC.LIGHTING, "interior evening", {"lamps_on": True, "sun_strength": 0.0})
    monkeypatch.setitem(PR.MOOD_WORDS, "interior evening", "Warm evening")
    out = PR.build_prompt(profile(lighting={"mood": "interior evening"}), "living", [], 18.0)
    assert out["lamps_on"] is True and "Warm evening light with the lamps switched on and the last daylight" in out["prompt"]
    assert "light through the windows" not in out["prompt"] and out["prompt"].endswith("sharp focus, 18 mm lens.")
    day = PR.build_prompt(profile(), "living", [], 18.0)
    assert day["lamps_on"] is False and "light through the windows" in day["prompt"]
    assert not PR.lamps_on(None) and not PR.lamps_on("no such mood")


# --------------------------------------------------------------------------
# The gate
# --------------------------------------------------------------------------

def scene(prof: dict, objects=(), materials=None) -> dict:
    return {"style_profile": prof, "objects": list(objects), "materials": materials or {},
            "cameras": [{"name": "cam_a", "room_id": "r1", "kind": "interior"}]}


def test_the_expected_colour_has_lab_and_chroma(colours):
    c = GC.expected_colour("warm greige")
    assert c["name"] == "warm greige" and c["linear_rgb"] == [0.48, 0.42, 0.35]
    assert 50 < c["lab"][0] < 80 and c["chroma"] > 3                 # a warm grey is not neutral
    assert GC.expected_colour("no such colour") is None and GC.expected_colour(None) is None
    assert GC.expected_colour("") is None


def test_a_paint_colour_is_a_flat_wall_with_its_expected_colour_recorded(colours):
    walls = GC.structure_albedo(scene(profile()), "r1")[GC.WALL_REGION]
    assert walls["albedo_mode"] == "flat" and walls["source"] == "vocabulary.MATERIALS"    # track C: paint is flat
    assert walls["colour"] == "warm greige" and walls["colour_chroma"] > 3 and len(walls["colour_lab"]) == 3
    assert walls["colour_linear_rgb"] == [0.48, 0.42, 0.35] and "colour_unknown" not in walls
    # The neutral check measures it (a flat wall), as the change of chroma, not as a distance from zero.
    out = GC.neutral_metrics({GC.WALL_REGION: [60.0, 5.0, 12.0]}, {GC.WALL_REGION: [60.0, 5.0, 18.0]},
                             {GC.WALL_REGION: 900}, 1000, {GC.WALL_REGION: walls}, 0.01)
    assert out["regions"][GC.WALL_REGION] == pytest.approx(
        abs((5.0 ** 2 + 18.0 ** 2) ** 0.5 - (5.0 ** 2 + 12.0 ** 2) ** 0.5), abs=1e-3)
    assert out["albedo"][GC.WALL_REGION]["colour"] == "warm greige"


def test_an_unknown_colour_phrase_is_listed_and_the_mode_is_not_guessed(colours):
    prof = profile(walls={"material": "paint", "asset": None, "colour": "dusty mauve"})
    walls = GC.structure_albedo(scene(prof), "r1")[GC.WALL_REGION]
    assert walls["colour"] == "dusty mauve" and walls["colour_unknown"] is True and "colour_chroma" not in walls
    # Track C's vocabulary says `paint` is flat; the unknown colour is listed, never guessed.
    assert walls["albedo_mode"] == "flat" and walls["source"] == "vocabulary.MATERIALS"
    plain = GC.structure_albedo(scene(profile(walls={"material": "plaster_white", "asset": None, "colour": None})),
                                "r1")[GC.WALL_REGION]
    assert plain["albedo_mode"] == "flat" and "colour" not in plain and "accent" not in plain


def test_a_textured_accent_wall_makes_the_walls_of_its_room_texture(colours):
    accent = {"material": "wood_slat", "asset": None, "colour": None, "room_types": ["living"], "rule": "r"}
    prof = profile(walls={"material": "plaster_white", "asset": None, "colour": None}, wall_accent=accent)
    materials = {"wood_slat__a": {"slug": "wood_slat", "albedo_mode": "texture", "textured": True}}
    # Track F's manifest: the accent wall object is flagged, lists the rooms that carry the face and its slot.
    walls_here = {"kind": "wall", "name": "w_1", "wenart_id": "w_1", "material": "plaster_white__x", "accent": True,
                  "room_ids": ["r1"], "accent_material": "wood_slat__a", "accent_reason": "behind the sofa"}
    walls_there = dict(walls_here, name="w_2", wenart_id="w_2", room_ids=["r2"])
    here = GC.structure_albedo(scene(prof, [walls_here, walls_there], materials), "r1")[GC.WALL_REGION]
    assert here["albedo_mode"] == "texture" and here["accent"]["in_room"] is True
    assert here["accent"]["slot"] == "wood_slat__a" and here["source"].startswith("wall_accent in this room")
    there = GC.structure_albedo(scene(prof, [walls_there], materials), "r1")[GC.WALL_REGION]
    assert there["albedo_mode"] == "flat" and there["accent"]["in_room"] is False
    # A plain wall object of the accent's material is not the accent: only the flagged object counts.
    plain = dict(walls_here, accent=False)
    assert GC.structure_albedo(scene(prof, [plain], materials), "r1")[GC.WALL_REGION]["albedo_mode"] == "flat"
    # A flat accent colour keeps the walls flat; a wet room has no accent wall.
    flat_acc = dict(accent, material="paint", colour="terracotta")
    flat_here = dict(walls_here, accent_material="paint__terracotta")
    flat = GC.structure_albedo(scene(profile(wall_accent=flat_acc), [flat_here], {}), "r1")[GC.WALL_REGION]
    assert flat["albedo_mode"] == "flat" and flat["accent"]["albedo_mode"] == "flat"
    wet = scene(prof, [walls_here, {"kind": "floor", "element_id": "r1", "wet": True, "name": "f", "wenart_id": "f"}],
                materials)
    assert "accent" not in GC.structure_albedo(wet, "r1")[GC.WALL_REGION]
