"""CPU tests of the TRELLIS.2 prompts and plans for the new types (docs/milestone10.md §4.5, §4.6, §7 pod L2:
``plan --target 20`` for furniture and 15 for decor).

Covered: a prompt for every type and every style family (all 9 families, so at least 3 per type), the hint groups of
the textile, plant, lighting and accessory types, the species and pot variants of the large floor plant, the Milestone
8 / 9 prompts and keys unchanged (pods L2 and L3 images are not rendered again), the per-type TRELLIS.2 settings, the
target plans of the new types, and the survey records of a variant (species, pot) down to the catalogue entry.
"""
import hashlib
import json
from pathlib import Path

import pytest

from test_generate import FakeImages, accepted_list, make_glb, quiet
from wenart.assets import generate as G
from wenart.assets import objaverse as OV

CFG = G.load_config()
FAMILIES = G.known_families()
OLD_TYPES = ("bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee", "desk", "chair", "wardrobe",
             "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower", "bathtub", "tv_unit", "bookshelf",
             "nightstand", "dresser", "washing_machine", "side_table", "floor_lamp", "potted_plant", "vase", "bowl",
             "plant_small")
NEW_FURNITURE = ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
                 "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
NEW_DECOR = ("curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture", "plant_large",
             "pendant_light", "ceiling_light")


def test_every_new_type_has_a_prompt_for_every_style_family():
    assert len(FAMILIES) == 9
    for t in NEW_FURNITURE + NEW_DECOR:
        for family in FAMILIES:
            text = G.prompt_for(t, family, CFG)
            assert text.startswith(f"a single {family} style ") and "plain white background" in text, (t, family)
            assert "{" not in text and "}" not in text, f"{t}/{family}: an unfilled slot: {text}"
        assert len({G.prompt_for(t, f, CFG) for f in FAMILIES}) == len(FAMILIES), f"{t}: the families give one prompt"
    assert set(NEW_FURNITURE) <= set(G.plan_types(CFG)) and set(NEW_DECOR) <= set(G.decor_types(CFG))
    assert G.target_types(CFG)[-len(G.decor_types(CFG)):] == G.decor_types(CFG)


def test_the_milestone_8_and_9_prompts_and_keys_are_unchanged():
    """Pods L2 and L3 rendered their images under these prompts (image keys hash the prompt, the seed and the
    settings): a changed word would render them all again. The digest is the sha256 prefix of the 27 x 9 prompts of
    commit 55174db."""
    lines = [G.prompt_for(t, f, CFG) for t in OLD_TYPES for f in FAMILIES]
    assert hashlib.sha256("\n".join(lines).encode()).hexdigest()[:16] == "ec4b5102398671a9"
    item = {"pair": "sofa__japandi", "type": "sofa", "family": "japandi", "index": 1,
            "prompt": G.prompt_for("sofa", "japandi", CFG), "seed": G.seed_for("sofa", "japandi", 1)}
    assert G.mesh_settings(CFG, item) == G.mesh_settings(CFG)             # furniture: the M8 settings
    assert G.mesh_settings(CFG, dict(item, type="vase")) == {**G.mesh_settings(CFG), **CFG["trellis_decor"]}


def test_hint_groups_follow_what_the_object_is_made_of():
    assert [G.hint_group(t, CFG) for t in ("sofa", "fridge", "vase", "curtain", "blind", "throw", "plant_large",
                                           "pendant_light", "ceiling_light", "books", "basket", "tray", "clock",
                                           "candle", "sculpture", "crib", "wall_cabinet")] == [
        "furniture", "fixtures", "decor", "textile", "textile", "textile", "plant", "lighting", "lighting",
        "accessory", "accessory", "accessory", "accessory", "decor", "decor", "furniture", "furniture"]
    for family in FAMILIES:
        for group in ("furniture", "fixtures", "decor", "textile", "plant", "lighting", "accessory"):
            assert CFG["family_hints"][family][group].strip(), (family, group)
    for t, group in CFG["hint_groups"].items():
        assert group in CFG["family_hints"]["modern"] and t in G.target_types(CFG)
    # a curtain is not described in ceramics, a lamp not in upholstery
    assert "ceramic" not in G.prompt_for("curtain", "modern", CFG)
    assert "linen" in G.prompt_for("curtain", "mediterranean", CFG) or "cotton" in G.prompt_for(
        "curtain", "mediterranean", CFG)


def test_large_plants_cycle_species_and_pots_over_images_and_families():
    seen = set()
    for family in FAMILIES:
        for index in range(1, 4):
            v = G.variant_for("plant_large", family, index, CFG)
            assert set(v["attributes"]) == {"species", "pot"} and set(v["values"]) == {"plant", "pot"}
            text = G.prompt_for("plant_large", family, CFG, index)
            assert v["values"]["plant"] in text and v["values"]["pot"] in text and "floor pot" in text
            seen.add((v["attributes"]["species"], v["attributes"]["pot"]))
    assert {s for s, _p in seen} == {"palm", "monstera", "fiddle-leaf fig", "olive", "fern"}     # the brief's species
    assert {p for _s, p in seen} >= {"rattan", "cream"}                                          # and its pots
    assert len(seen) >= 12
    assert G.prompt_for("plant_large", "modern", CFG, 1) != G.prompt_for("plant_large", "modern", CFG, 2)
    assert G.variant_for("sofa", "modern", 1, CFG) is None and G.variant_for("vase", "modern", 3, CFG) is None
    assert G.prompt_for("sofa", "modern", CFG, 1) == G.prompt_for("sofa", "modern", CFG, 5)      # one prompt per pair


def test_trellis_settings_per_decor_type():
    base = G.mesh_settings(CFG)
    for t in CFG["trellis_decor_full"]:
        assert t in CFG["decor_types"] and G.mesh_settings(CFG, {"type": t}) == base, t           # thin leaves, folds
    for t in ("candle", "clock", "books", "pendant_light", "ceiling_light", "vase"):
        assert G.mesh_settings(CFG, {"type": t})["pipeline_type"] == "512", t
    assert base["pipeline_type"] == "1024_cascade"


# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------

def test_the_target_plan_covers_the_new_types_with_their_own_prompts(tmp_path):
    empty = accepted_list(tmp_path / "accepted.json", [])
    doc = G.make_target_plan([empty], FAMILIES, tmp_path / "lib", CFG, target=15,
                             types=["clock", "plant_large", "crib"], log=quiet)
    assert doc["mode"] == "target" and doc["counts"]["types_short"] == 3
    per = doc["per_type"]
    assert all(per[t]["deficit"] == 15 and per[t]["new"] == 22 for t in per)       # ceil(15 / 0.7) candidates
    items = {(p["type"], p["family"], it["index"]): it for p in doc["pairs"] for it in p["items"]}
    assert len(items) == 66
    plant = [it for (t, _f, _i), it in items.items() if t == "plant_large"]
    assert len({it["prompt"] for it in plant}) >= 12                                # species and pots vary
    clock = [it for (t, _f, _i), it in items.items() if t == "clock"]
    assert len({it["prompt"] for it in clock}) == len(FAMILIES)                      # one prompt per family
    for (t, f, i), it in items.items():
        assert it["prompt"] == G.prompt_for(t, f, CFG, i) and it["seed"] == G.seed_for(t, f, i)
    got = G.plan_items(doc, CFG)
    assert len(got) == 66 and {it["type"] for it in got} == {"clock", "plant_large", "crib"}


def test_the_gap_plan_gives_a_variant_type_one_prompt_per_image(tmp_path):
    empty = accepted_list(tmp_path / "accepted.json", [])
    doc = G.make_plan([empty], ["modern"], tmp_path / "lib", CFG, types=["bunk_bed", "sofa_corner"], log=quiet)
    assert {p["type"] for p in doc["pairs"]} == {"bunk_bed", "sofa_corner"} and "prompts" not in doc["pairs"][0]
    # plant_large is a decor type: the gap plan lists furniture types, the target plan the decor ones
    with pytest.raises(G.UsageError):
        G.parse_types("plant_large", CFG)
    assert G.parse_types("plant_large", CFG, target=True) == ["plant_large"]
    pair = {"pair": G.pair_id("plant_large", "modern"), "type": "plant_large", "family": "modern",
            "prompt": G.prompt_for("plant_large", "modern", CFG), "seeds": [1, 2]}
    items = G.plan_items({"pairs": [dict(pair, prompts=[G.prompt_for("plant_large", "modern", CFG, i)
                                                       for i in (1, 2)])], "images_per_pair": 2}, CFG)
    assert [it["prompt"] for it in items] == [G.prompt_for("plant_large", "modern", CFG, i) for i in (1, 2)]
    again = G.plan_items({"pairs": [pair], "images_per_pair": 2}, CFG)               # a plan without per-image prompts
    assert again[0]["prompt"] != again[1]["prompt"]                                  # still one per image


# --------------------------------------------------------------------------
# A run: the survey record of a variant, its catalogue entry
# --------------------------------------------------------------------------

class SettingsMeshes:
    """TRELLIS.2 stand-in that accepts the ``settings`` of decor items."""

    def __init__(self, calls):
        self.calls = calls

    def __call__(self, cfg):
        return self

    def load(self):
        pass

    def image_to_glb(self, image_path, glb_path, seed, **kw):
        self.calls.append((Path(image_path).parent.name, seed, kw.get("settings", {}).get("pipeline_type")))
        make_glb(Path(glb_path), triangles=1500, textured=True, salt=seed)
        return {}

    def versions(self):
        return {"fake": True}

    def close(self):
        pass


def test_a_generated_large_plant_keeps_its_species_and_pot_down_to_the_catalogue(tmp_path):
    empty = accepted_list(tmp_path / "accepted.json", [])
    doc = G.make_target_plan([empty], ["mediterranean"], tmp_path / "lib", CFG, target=2, rate=1.0,
                             types=["plant_large", "candle"], log=quiet)
    plan = tmp_path / "lib" / "generate" / "plan.json"
    calls, mesh_calls = [], []
    rc = G.run(tmp_path / "lib", plan, cfg=CFG, image_backend=FakeImages(calls), mesh_backend=SettingsMeshes(mesh_calls),
               log=quiet)
    assert rc == 0 and len(doc["pairs"]) == 2
    survey = json.loads((tmp_path / "lib" / G.SURVEY_NAME).read_text())
    plants = [c for c in survey["candidates"] if c["group"] == "plant_large"]
    candles = [c for c in survey["candidates"] if c["group"] == "candle"]
    assert len(plants) == 2 and len(candles) == 2
    assert {c["kind"] for c in plants + candles} == {"decor"} and plants[0]["decor_type"] == "plant_large"
    species = [c["attributes"]["species"] for c in plants]
    assert species == ["palm", "monstera"] or len(set(species)) == 2
    assert all(c["attributes"]["species"] in c["generated"]["prompt"] for c in plants)
    assert "attributes" not in candles[0]
    by_pair = {call[0]: call[2] for call in mesh_calls}                  # the settings override each pair was given
    assert by_pair == {"plant_large__mediterranean": None, "candle__mediterranean": "512"}
    # the catalogue entry keeps them (objaverse.catalog_entry; decor type decor_plant_large)
    cand = plants[0]
    obj = {"unit": {"scale": 1.0, "note": "n", "ok": True},
           "measure": {"bbox_min_raw": [0, 0, 0], "bbox_max_raw": [0.6, 0.6, 1.5], "triangles": 1500, "vertices": 900}}
    dec = {"type": "plant_large", "kind": "decor", "decor_type": "plant_large", "front_axis": "-Y",
           "front_axis_confidence": "low", "front_axis_note": "none", "styles": ["mediterranean"], "style_note": "s",
           "quality": [5, 4], "licence_flag": None}
    entry = OV.catalog_entry(cand, obj, dec, cand["glb_sha256"], OV.load_config())
    assert entry["species"] == cand["attributes"]["species"] and entry["pot"] == cand["attributes"]["pot"]
    assert entry["type"] == "decor_plant_large" and entry["generated"]["prompt"] == cand["generated"]["prompt"]
