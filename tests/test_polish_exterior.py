"""Polish of exterior views (Milestone 10, docs/milestone10.md §3.3 items 3 and 5): the exterior prompt and the
per-kind (interior / exterior) gate decision of the runner.

What: the words of the outside looks (every slug the build can resolve has prompt words; colours, ``brick_*``,
``painted:<colour>`` and ``render:<colour>`` are built from their colour word; an unknown slug is a warning), and the
runner with a toy project that has one exterior camera next to its rooms: an exterior validation that does not allow
the polish keeps the exterior view Cycles only (reason ``gate``, no attempt, no gate reference, no model prompt)
and leaves the rooms alone; an allowing one polishes it with the exterior prompt.

Why: a failed exterior validation must never switch off the rooms (the per-kind decision) and an outside view must
never reach the model with a room prompt.

How: the toy project of ``test_polish_run`` plus an ``ext_1`` camera (kind ``exterior``, no room, ``exterior_looks``
in the scene manifest); fakes for the backend, the gate and the exterior decision.
"""
from __future__ import annotations

import json
import sys
import types
from pathlib import Path

import test_polish_run as T
from wenart import views as V
from wenart.blender import exterior as BE
from wenart.blender import shell
from wenart.gate import calibrate as CAL
from wenart.gate import validate as VAL
from wenart.polish import prompt as PR
from wenart.polish.runner import is_exterior_camera, run_polish
from wenart.polish.schema import validate_manifest
from wenart.style import vocabulary as VOC

LOOKS = {"facade": {"material": "render", "colour": "greige", "source": "fallback", "assumed": True},
         "roof": {"material": "concrete_tiles", "colour": "anthracite", "source": "fallback", "assumed": True},
         "window_frame": {"material": "dark_bronze", "colour": "dark bronze", "source": "brief", "assumed": False},
         "door": {"material": "wood_oak_light", "colour": None, "source": "fallback", "assumed": True},
         "paving": {"material": "paving", "colour": "grey", "source": "fallback", "assumed": True},
         "garden": {"material": "grass", "colour": None, "source": "fallback", "assumed": True}}
PROFILE = {"family": "modern", "lighting": {"mood": "warm daylight"}}


# --------------------------------------------------------------------------
# The prompt
# --------------------------------------------------------------------------

def test_the_exterior_prompt_names_the_looks_the_view_and_the_lens():
    r = PR.build_exterior_prompt(PROFILE, LOOKS, 28.0, "corner")
    assert r["warnings"] == [] and r["view_kind"] == "exterior" and r["lens_mm"] == 28.0
    p = r["prompt"]
    assert p.startswith("Photorealistic architectural photograph of a house exterior in modern style, seen from a "
                        "corner of the plot at eye level")
    for words in ("Greige smooth rendered facade", "anthracite concrete tile roof", "dark bronze window frames",
                  "grey concrete paver paving", "lawn garden"):
        assert words in p, words
    assert p.endswith("Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and "
                      "textures, sharp focus, 28 mm lens.")
    # Nothing of the interior prompt reaches an outside view.
    assert "interior" not in p and "walls" not in p and "through the windows" not in p


def test_each_view_kind_has_its_own_words():
    texts = {v: PR.build_exterior_prompt(PROFILE, LOOKS, 28.0, v)["prompt"] for v in ("corner", "aerial", "elevation")}
    assert len(set(texts.values())) == 3
    assert "aerial" in texts["aerial"] and "straight on" in texts["elevation"]
    none = PR.build_exterior_prompt(PROFILE, LOOKS, 28.0, None)
    assert "from outside" in none["prompt"] and none["warnings"] == []
    odd = PR.build_exterior_prompt(PROFILE, LOOKS, 28.0, "balloon")
    assert any("balloon" in w for w in odd["warnings"])


def test_every_slug_the_build_can_resolve_has_exterior_words():
    """A new slug without words fails here instead of reaching a prompt as a raw slug."""
    from wenart.style import finishes as FIN                 # track C's exterior slugs per slot (Milestone 10)
    slugs = {slot: set(names) for slot, names in FIN.EXTERIOR_MATERIALS.items()}
    for slot, fb in BE.EXTERIOR_FALLBACK.items():
        if isinstance(fb, dict):
            slugs.setdefault(slot, set()).add(fb["material"])
    slugs["window_frame"] |= {"pvc_white", "aluminium_anthracite", "steel_black", "dark_bronze", "oak",
                              "painted_metal_white"}
    slugs["facade"] |= {"concrete_exposed", "plaster_exterior"}
    for slot, names in slugs.items():
        for slug in sorted(names):
            warnings: list = []
            words = PR.exterior_material_words(slug, None, warnings)
            assert words and warnings == [], (slot, slug, warnings)
            assert slug in PR.EXTERIOR_MATERIAL_WORDS or slug in PR.MATERIAL_WORDS, (slot, slug)
    # The flat-colour table of the shell lists the same outside slugs: none may be missing here.
    for slug in shell.LOOK_RGB:
        if slug in ("bark", "foliage", "soffit"):          # trees and the soffit are not named in the prompt
            continue
        warnings = []
        PR.exterior_material_words(slug, None, warnings)
        assert warnings == [], slug


def test_slugs_with_a_colour_inside_are_built_from_it():
    w: list = []
    assert PR.exterior_material_words("brick_yellow", None, w) == "yellow brick"
    assert PR.exterior_material_words("brick_dark_red", None, w) == "dark red brick"
    assert PR.exterior_material_words("painted:sage", None, w) == "sage painted"
    assert PR.exterior_material_words("render:light_grey", None, w) == "light grey smooth rendered"
    assert w == []
    # A colour name is not said twice, and goes in front when the material does not hold it.
    assert PR.exterior_material_words("dark_bronze", "dark bronze", w) == "dark bronze"
    assert PR.exterior_material_words("render", "greige", w) == "greige smooth rendered"
    assert PR.exterior_material_words("brick_red", "red", w) == "red brick"
    assert PR.exterior_material_words(None) is None


def test_an_unknown_slug_is_used_as_words_and_listed():
    w: list = []
    assert PR.exterior_material_words("glass_brick", None, w) == "glass brick"
    assert w and "glass_brick" in w[0]
    r = PR.build_exterior_prompt(PROFILE, {"facade": {"material": "weird_slug", "colour": None}}, 28, "corner")
    assert "Weird slug facade" in r["prompt"] and any("weird_slug" in x for x in r["warnings"])


def test_every_lighting_mood_has_exterior_words():
    for mood in VOC.LIGHTING:
        w: list = []
        text = PR.exterior_mood_words(mood, w)
        assert text and w == [], mood
    w = []
    assert PR.exterior_mood_words(None, w) .startswith("Natural") and w
    w = []
    assert PR.exterior_mood_words("moonlit", w) == "Moonlit light" and w


def test_missing_looks_and_family_are_warnings_not_guesses():
    r = PR.build_exterior_prompt({}, None, None, "corner")
    text = " ".join(r["warnings"])
    for part in ("no style family", "no light mood", "no exterior looks", "no camera lens"):
        assert part in text, part
    assert "window frames" not in r["prompt"] and "roof" not in r["prompt"] and "mm lens" not in r["prompt"]


def test_the_looks_of_resolve_looks_go_through_the_prompt_without_warnings():
    """The real resolver output (brief words, fallback colours from the style's walls) reads cleanly."""
    looks = BE.resolve_looks({}, {"walls": {"colour": "greige"}},
                             {"exterior": {"window_frame": "dark bronze window frames", "facade": "brick facade",
                                           "roof": "standing seam metal roof", "paving": "gravel"}})
    r = PR.build_exterior_prompt(PROFILE, looks, 24, "aerial")
    assert r["warnings"] == [], r["warnings"]
    assert "red brick facade" in r["prompt"].lower() and "standing-seam metal roof" in r["prompt"]
    assert "gravel paving" in r["prompt"]


# --------------------------------------------------------------------------
# The runner
# --------------------------------------------------------------------------

def make_ext_project(root: Path) -> Path:
    """The toy project of test_polish_run plus the exterior camera ``ext_1``."""
    out = T.make_project(root)
    renders = out / "renders"
    rgb, index, depth, normal = T.passes("cam_a")
    cam = "ext_1"
    V.write_png_rgb(renders / f"{cam}.png", rgb)
    V.write_png16(renders / f"{cam}_index.png", index)
    V.write_png16(renders / f"{cam}_depth_mm.png", depth)
    V.write_png_rgb(renders / f"{cam}_normal.png", V.encode_normal(normal, V.normal_hit(normal)))
    stats = {str(k): v for k, v in V.compute_index_stats(index).items()}
    manifest = json.loads((renders / "render_manifest.json").read_text(encoding="utf-8"))
    manifest["renders"].insert(3, {
        "camera": cam, "png": f"{cam}.png", "index_png": f"{cam}_index.png", "resolution": [T.W, T.H],
        "room_id": None, "level_id": None, "index_stats": stats,
        "files": {"depth_mm": f"{cam}_depth_mm.png", "normal": f"{cam}_normal.png"},
        "render_key": "0123456789abcdef", "hidden": [], "plugged": []})
    (renders / "render_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    path = out / "scene" / "scene_manifest.json"
    scene = json.loads(path.read_text(encoding="utf-8"))
    scene["cameras"].append({"name": cam, "kind": "exterior", "room_id": None, "level_id": None, "lens_mm": 28.0,
                             "view": "corner", "variant": "base"})
    scene["exterior_looks"] = LOOKS
    path.write_text(json.dumps(scene), encoding="utf-8")
    return out


def decision(name: str, allowed: bool, reasons=()):
    def exterior_polish(project_out, *args, **kwargs):
        exterior_polish.calls.append(Path(project_out).name)
        return {"decision": name, "polish_allowed": allowed, "reasons": list(reasons), "benign_accept": 0.9,
                "negative_reject": 0.5 if not allowed else 1.0, "n_benign": 8, "n_negative": 12,
                "source": "gate_calibration.json"}
    exterior_polish.calls = []
    return exterior_polish


def run(out, exterior_polish):
    deps, backend, gate = T.make_deps()
    deps.exterior_polish = exterior_polish
    m = run_polish(out, "run", deps=deps)
    return m, backend, gate


def test_a_failed_exterior_validation_keeps_the_exterior_views_cycles_only(tmp_path):
    out = make_ext_project(tmp_path)
    ext = decision("polish_disabled", False, ["too many exterior geometry changes get through (0.50 < 0.80)"])
    m, backend, gate = run(out, ext)
    assert validate_manifest(m) == []
    e = T.view_of(m, "ext_1")
    assert (e["final"], e["final_attempt"], e["reason"]) == ("cycles", None, "gate")
    assert e["attempts"] == [] and e["view_kind"] == "exterior" and e["room_id"] is None
    assert any("polish_disabled" in n and "0.50 < 0.80" in n for n in e["notes"])
    # The rooms are polished as before: the exterior decision is per kind.
    for cam in ("cam_a", "cam_b", "cam_c"):
        assert T.view_of(m, cam)["view_kind"] == "interior"
    assert T.view_of(m, "cam_a")["final"] == "polished"
    # Nothing was made for the held view: no gate reference, no model prompt.
    assert "ext_1" not in gate.prepared and "ext_1" not in gate.compared
    sent = [p for call in backend.ready for p in call]
    assert sent and all("house exterior" not in p for p in sent) and all("house exterior" not in c["prompt"]
                                                                          for c in backend.calls)
    assert not (out / "polish" / "ext_1_a1.png").exists() and not (out / "polish" / "ext_1_control_depth.png").exists()
    # The decision is recorded.
    g = m["exterior_gate"]
    assert g["decision"] == "polish_disabled" and g["polish_allowed"] is False
    assert g["views"] == ["ext_1"] and g["held"] == ["ext_1"] and g["negative_reject"] == 0.5
    assert any("exterior gate polish_disabled" in w for w in m["warnings"])
    assert ext.calls == ["toy"]


def test_an_allowing_exterior_validation_polishes_the_exterior_view_with_its_own_prompt(tmp_path):
    out = make_ext_project(tmp_path)
    m, backend, gate = run(out, decision("ok", True))
    assert validate_manifest(m) == []
    e = T.view_of(m, "ext_1")
    assert (e["final"], e["reason"]) == ("polished", None) and e["view_kind"] == "exterior"
    assert e["expected_source"] == "exterior_looks"
    assert e["prompt"].startswith("Photorealistic architectural photograph of a house exterior in Scandinavian style")
    assert e["prompt"].endswith("sharp focus, 28 mm lens.") and "facade" in e["prompt"]
    assert "ext_1" in gate.prepared
    assert any("house exterior" in c["prompt"] for c in backend.calls)
    # The interior views keep their room prompts.
    assert T.view_of(m, "cam_a")["prompt"].startswith("Photorealistic interior photograph of a living room")
    g = m["exterior_gate"]
    assert g["polish_allowed"] is True and g["held"] == [] and g["views"] == ["ext_1"]
    # The determinism view is a room, never the exterior view.
    assert json.loads((out / "polish" / "determinism.json").read_text(encoding="utf-8"))["camera"] in (
        "cam_a", "cam_b", "cam_c")


def test_an_unreadable_exterior_decision_never_allows_the_polish(tmp_path):
    out = make_ext_project(tmp_path)

    def broken(project_out):
        raise OSError("gate_calibration.json is damaged")

    m, _, gate = run(out, broken)
    e = T.view_of(m, "ext_1")
    assert (e["final"], e["reason"]) == ("cycles", "gate")
    assert m["exterior_gate"]["decision"] == "not_validated" and m["exterior_gate"]["polish_allowed"] is False
    assert any("damaged" in r for r in m["exterior_gate"]["reasons"])
    assert "ext_1" not in gate.prepared


def test_a_project_without_exterior_views_never_asks_for_the_exterior_decision(tmp_path):
    out = T.make_project(tmp_path)
    ext = decision("ok", True)
    m, _, _ = run(out, ext)
    assert m["exterior_gate"] is None and ext.calls == []
    assert all(v["view_kind"] == "interior" for v in m["views"])


def test_the_brief_polish_false_holds_the_exterior_views_too(tmp_path, monkeypatch):
    out = make_ext_project(tmp_path)
    brief = types.ModuleType("wenart.brief")
    brief.load_brief = lambda project_dir: {"values": {"polish": False}, "assumed": []}
    monkeypatch.setitem(sys.modules, "wenart.brief", brief)
    ext = decision("ok", True)
    m, backend, _ = run(out, ext)
    assert all(v["final"] == "cycles" and v["reason"] == "brief" for v in m["views"])
    assert ext.calls == [] and backend.calls == [] and m["exterior_gate"] is None


def test_is_exterior_camera_follows_the_scene_manifest():
    scene = {"cameras": [{"name": "ext_1", "kind": "exterior", "room_id": None},
                         {"name": "cam_a", "kind": "interior", "room_id": "r1"},
                         {"name": "ext_9", "room_id": None}, {"name": "cam_x", "room_id": None}]}
    assert is_exterior_camera(scene, "ext_1") and not is_exterior_camera(scene, "cam_a")
    assert is_exterior_camera(scene, "ext_9")                    # no kind: the name and no room decide
    assert not is_exterior_camera(scene, "cam_x")


def test_a_variant_sub_output_reads_the_base_projects_calibration(tmp_path):
    base = tmp_path / "outputs" / "p"
    sub = base / "variants" / "l-1b-acik-mutfak"
    (base / "gate").mkdir(parents=True)
    sub.mkdir(parents=True)
    # A calibration of a project that rendered no exterior view: found in the base, decision not_applicable.
    (base / "gate" / VAL.CALIBRATION_NAME).write_text(json.dumps({"exterior": {"cameras_rendered": 0}}),
                                                      encoding="utf-8")
    own = CAL.exterior_polish(sub)
    assert own["decision"] == "not_applicable" and own["polish_allowed"] is False and own["from_base_project"]
    # The base project itself is not "from the base".
    assert CAL.exterior_polish(base)["from_base_project"] is False
    # Without any file: not validated.
    none = CAL.exterior_polish(tmp_path / "outputs" / "q")
    assert none["decision"] == "not_validated" and none["source"] is None
