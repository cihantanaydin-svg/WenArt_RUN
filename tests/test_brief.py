"""CPU tests for wenart.brief (docs/milestone5.md §1.1, §6): brief.yaml merged over the defaults.yaml brief block."""
from pathlib import Path

import pytest
import yaml

from wenart import brief as B
from wenart import views as VW

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"


def test_defaults_block_has_the_m5_keys():
    block = yaml.safe_load((ROOT / "wenart" / "defaults.yaml").read_text(encoding="utf-8"))["brief"]
    assert block["polish"] is True
    assert block["style_photos"] == []
    assert block["decor"] is True and block["empty_rooms"] == "ai"
    assert B.brief_defaults() == block


def test_synthetic_brief_keeps_its_style_and_assumes_the_rest():
    brief = B.load_brief(PROJECTS / "synthetic-01")
    assert set(brief) == {"values", "assumed", "path", "warnings"}
    v = brief["values"]
    assert v["style"].startswith("Scandinavian") and v["polish"] is True and v["style_photos"] == []
    # Milestone 8: render.lens_mm (auto = 18 mm, 16 mm in rooms narrower than 2.2 m) is listed as assumed too.
    assert v["render"] == {"views_per_room": 3, "resolution": [1920, 1080], "samples": 256, "lens_mm": "auto"}
    assert "style" not in brief["assumed"]
    assert brief["assumed"] == ["empty_rooms", "decor", "polish", "style_photos", "ceiling_height",
                                "render.views_per_room", "render.resolution", "render.samples", "render.lens_mm"]
    assert brief["warnings"] == [] and brief["path"].endswith("brief.yaml")
    styles = B.load_brief(PROJECTS / "synthetic-03")["values"]["styles"]
    assert len(styles) == 2


def test_missing_brief_gives_defaults_and_says_so(tmp_path):
    brief = B.load_brief(tmp_path / "nothing_here")
    assert brief["values"]["polish"] is True and brief["path"] is None
    assert "polish" in brief["assumed"] and "render.samples" in brief["assumed"]
    assert len(brief["warnings"]) == 1 and "every brief value is a default" in brief["warnings"][0]
    assert B.load_brief(PROJECTS / "synthetic-02")["path"] is None      # the photo project has no brief.yaml


def test_brief_values_win_and_nested_blocks_merge_key_by_key(tmp_path):
    (tmp_path / "brief.yaml").write_text(
        "style: oak floor\npolish: false\nstyle_photos: [a.jpg, b.jpg]\nrender:\n  samples: 64\n  extra: 1\n"
        "custom_key: 7\n", encoding="utf-8")
    brief = B.load_brief(tmp_path)
    v = brief["values"]
    assert v["polish"] is False and v["style_photos"] == ["a.jpg", "b.jpg"] and v["custom_key"] == 7
    assert v["render"] == {"views_per_room": 3, "resolution": [1920, 1080], "samples": 64, "lens_mm": "auto",
                           "extra": 1}
    assert "polish" not in brief["assumed"] and "style_photos" not in brief["assumed"]
    assert "render.samples" not in brief["assumed"] and "render.views_per_room" in brief["assumed"]
    assert brief["warnings"] == []
    assert B.value(brief, "render.samples") == 64 and B.value(brief, "render.nope", "d") == "d"
    assert B.is_assumed(brief, "decor") and not B.is_assumed(brief, "polish") and B.is_assumed(None, "polish")


@pytest.mark.parametrize("text, key, problem", [
    ("polish: 'no'\n", "polish", "expected bool"),
    ("style_photos: photo.jpg\n", "style_photos", "expected list"),
    ("style_photos: [1, 2]\n", "style_photos", "list of file names"),
    ("decor: 3\n", "decor", "expected bool"),
    ("render: 5\n", "render.samples", "expected dict"),
    ("polish:\n", "polish", "empty"),
])
def test_wrong_types_are_not_used_and_are_reported(tmp_path, text, key, problem):
    (tmp_path / "brief.yaml").write_text(text, encoding="utf-8")
    brief = B.load_brief(tmp_path)
    assert key in brief["assumed"]
    assert any(problem in w for w in brief["warnings"]), brief["warnings"]
    assert B.value(brief, key) == B.value({"values": B.brief_defaults()}, key)


def test_non_mapping_brief_and_yaml_errors(tmp_path):
    (tmp_path / "brief.yaml").write_text("- just\n- a list\n", encoding="utf-8")
    brief = B.load_brief(tmp_path)
    assert brief["values"]["polish"] is True and "not a mapping" in brief["warnings"][0]
    (tmp_path / "brief.yaml").write_text("style: [unclosed\n", encoding="utf-8")
    with pytest.raises(yaml.YAMLError):
        B.load_brief(tmp_path)                           # a broken brief is never replaced by defaults silently
    (tmp_path / "brief.yaml").write_text("", encoding="utf-8")
    assert B.load_brief(tmp_path)["warnings"] == []      # an empty file is a brief without keys


def test_merge_brief_is_pure():
    defaults = {"a": 1, "b": {"c": True}}
    out = B.merge_brief({"b": {"c": False}}, defaults)
    assert out["values"] == {"a": 1, "b": {"c": False}} and out["assumed"] == ["a"]
    out["values"]["b"]["c"] = "changed"
    assert defaults == {"a": 1, "b": {"c": True}}


def test_project_paths_loads_the_brief(tmp_path):
    """wenart.views.project_paths (F0) picks up wenart.brief now that it exists."""
    import json
    out = tmp_path / "outputs" / "toy"
    (out / "scene").mkdir(parents=True)
    building = {"project": {"id": "toy", "source_folder": "projects/synthetic-01"}}
    (out / "building_final.json").write_text(json.dumps(building), encoding="utf-8")
    scene = {"project": "toy", "building": str(out / "building_final.json"), "objects": [], "cameras": []}
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene), encoding="utf-8")
    paths = VW.project_paths(out)
    assert paths["brief"]["values"]["style"].startswith("Scandinavian")
    assert not any("wenart.brief" in w for w in paths["warnings"])


# --------------------------------------------------------------------------
# Milestone 8 (docs/milestone8.md §5): render.lens_mm
# --------------------------------------------------------------------------

def test_lens_default_is_auto_and_listed_as_assumed(tmp_path):
    assert B.brief_defaults()["render"]["lens_mm"] == "auto"
    brief = B.load_brief(tmp_path / "nothing_here")
    assert B.value(brief, "render.lens_mm") == "auto" and "render.lens_mm" in brief["assumed"]
    assert B.lens_mm(brief) is None and B.lens_mm(None) is None          # auto: the 18 / 16 mm rule


@pytest.mark.parametrize("text, value", [("14", 14.0), ("18", 18.0), ("22.5", 22.5), ("35", 35.0), ("auto", None)])
def test_brief_lens_is_used_when_valid(tmp_path, text, value):
    (tmp_path / "brief.yaml").write_text(f"render:\n  lens_mm: {text}\n", encoding="utf-8")
    brief = B.load_brief(tmp_path)
    assert brief["warnings"] == [] and "render.lens_mm" not in brief["assumed"]
    assert B.lens_mm(brief) == value
    assert "render.samples" in brief["assumed"]                         # the other render keys stay defaults


@pytest.mark.parametrize("text", ["13.9", "36", "0", "-18", "wide", "[18]", "true", ".nan"])
def test_brief_lens_outside_14_to_35_is_reported_and_not_used(tmp_path, text):
    (tmp_path / "brief.yaml").write_text(f"render:\n  lens_mm: {text}\n", encoding="utf-8")
    brief = B.load_brief(tmp_path)
    assert B.value(brief, "render.lens_mm") == "auto" and B.lens_mm(brief) is None
    assert "render.lens_mm" in brief["assumed"]
    (w,) = brief["warnings"]
    assert w.startswith("brief.yaml render.lens_mm: expected auto or a lens from 14 to 35 mm") and "'auto' used" in w
    order = brief["assumed"]
    assert order.index("render.samples") < order.index("render.lens_mm")    # still in defaults.yaml order

