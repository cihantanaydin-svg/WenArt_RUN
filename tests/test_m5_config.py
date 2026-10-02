"""CPU tests for the Milestone 5 config files and package skeletons (docs/milestone5.md §1.3, §1.4, §1.6).

Every YAML loads; the model ids, revisions, licences and files in
``polish.yaml``, ``gate/models.yaml`` and ``vision_check/check.yaml`` equal
the table in docs/milestone5.md §1.6 (parsed from the markdown, so the spec
and the configs cannot drift); ``thresholds.yaml`` equals the §4.2 block; the
vendored ControlNet config matches its recorded sha256; the style photo
fixture is a byte copy of the M4 render; the skeleton packages import
without torch and expose the binding signatures.
"""
import hashlib
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from wenart.gate import api as gate_api
from wenart.polish import config as polish_config
from wenart.vision_check import config as check_config
from wenart.vision_check import expected

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "milestone5.md"


def spec_section(heading: str) -> str:
    """Text of the spec section that starts with ``heading`` up to the next heading of any level."""
    text = SPEC.read_text(encoding="utf-8")
    start = text.index(heading)
    rest = text[start + len(heading):]
    nxt = re.search(r"^#{2,4} ", rest, flags=re.M)
    return rest[: nxt.start()] if nxt else rest


def model_table() -> dict:
    """``{role: {"repo", "revision", "licence", "files": [..]}}`` from the §1.6 markdown table."""
    rows = {}
    for line in spec_section("### 1.6").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6 or cells[0] in ("Role", "") or set(cells[0]) <= {"-"}:
            continue
        rows[cells[0]] = {"repo": cells[1].strip("`"), "revision": cells[2].strip("`"), "licence": cells[3],
                          "files": re.findall(r"`([^`]+)`", cells[4])}
    return rows


def load(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def test_every_yaml_of_the_package_loads():
    files = sorted((ROOT / "wenart").rglob("*.yaml"))
    names = {f.relative_to(ROOT).as_posix() for f in files}
    assert {"wenart/polish/polish.yaml", "wenart/gate/models.yaml", "wenart/gate/thresholds.yaml",
            "wenart/vision_check/check.yaml"} <= names
    for f in files:
        assert isinstance(yaml.safe_load(f.read_text(encoding="utf-8")), dict), f


def test_spec_table_parses():
    table = model_table()
    assert set(table) == {"polish base", "polish control", "gate depth", "gate masks", "gate features",
                          "check pass 1", "check pass 2"}
    for row in table.values():
        assert re.fullmatch(r"[0-9a-f]{40}", row["revision"]), row


def test_model_revisions_equal_the_spec_table():
    table = model_table()
    polish = polish_config.load_config()["models"]
    gate = gate_api.load_models_config()["models"]
    check = check_config.load_config()["models"]
    pairs = [("polish base", polish["base"]), ("polish control", polish["controlnet"]),
             ("gate depth", gate["depth"]), ("gate masks", gate["sam"]), ("gate features", gate["dino"])]
    for role, cfg in pairs:
        row = table[role]
        assert (cfg["repo"], cfg["revision"], cfg["licence"]) == (row["repo"], row["revision"], row["licence"]), role
        assert cfg["allow_patterns"] == row["files"], role
    assert polish["controlnet"]["files"] == table["polish control"]["files"]
    for role, key in (("check pass 1", "qwen"), ("check pass 2", "glm")):
        row = table[role]
        cfg = check[key]
        assert (cfg["id"], cfg["revision"], cfg["licence"]) == (row["repo"], row["revision"], row["licence"]), role
    assert set(gate) == {"depth", "sam", "dino"} and set(polish) == {"base", "controlnet"}


def test_thresholds_equal_the_spec_block():
    block = re.search(r"```yaml\n(.*?)```", spec_section("### 4.2"), flags=re.S).group(1)
    assert gate_api.load_thresholds() == yaml.safe_load(block)
    assert gate_api.THRESHOLDS_PATH == ROOT / "wenart" / "gate" / "thresholds.yaml"


def test_polish_config_ladder_and_grids():
    cfg = polish_config.load_config()
    assert polish_config.CONFIG_PATH == ROOT / "wenart" / "polish" / "polish.yaml"
    assert (cfg["seed"], cfg["steps"], cfg["size"], cfg["determinism_view"]) == (0, 8, "native", None)
    keys = ("strength", "control", "scale", "size", "mode")
    assert [tuple(a[k] for k in keys) for a in cfg["ladder"]] == [
        (0.375, "depth", 0.8, "native", "plain"), (0.25, "depth", 0.8, "native", "plain"),
        (0.125, "depth", 0.8, "native", "plain")]
    sweep = cfg["grids"]["sweep"]
    grid = [a for a in sweep if a["role"] == "grid"]
    bad = [a for a in sweep if a["role"] == "presumed_bad"]
    assert len(sweep) == 11 and len(grid) == 10 and len(bad) == 1
    expected_grid = {(s, "depth", "native", "plain") for s in (0.125, 0.25, 0.375, 0.5)}
    expected_grid |= {(s, c, "native", "plain") for s in (0.25, 0.375) for c in ("canny", "geometry")}
    expected_grid |= {(0.375, "depth", "1536x864", "plain"), (0.375, "depth", "native", "anchor")}
    assert {(a["strength"], a["control"], a["size"], a["mode"]) for a in grid} == expected_grid
    assert all(a["scale"] == 0.8 for a in grid)
    assert bad[0]["strength"] == 0.75 and bad[0]["control"] is None
    smoke = cfg["grids"]["smoke"]
    assert [(a["strength"], a["control"]) for a in smoke] == [(0.25, "depth"), (0.375, "depth"),
                                                               (0.375, "canny"), (0.375, "geometry")]
    for attempt in cfg["ladder"] + grid + smoke:
        size = attempt["size"]
        assert size == "native" or all(int(v) % 16 == 0 for v in size.split("x"))


def test_vendored_controlnet_config_matches_its_source_record():
    cfg = polish_config.load_config()
    folder = polish_config.config_dir(cfg)
    assert folder == ROOT / "wenart" / "polish" / "configs" / "controlnet_union_2.1"
    data = (folder / "config.json").read_bytes()
    source = (folder / "SOURCE.md").read_text(encoding="utf-8")
    sha = re.search(r"sha256 \| `([0-9a-f]{64})`", source).group(1)
    assert hashlib.sha256(data).hexdigest() == sha and len(data) == 591
    assert "5d85f6a430fd40300f931bd1291e0c4982094859" in source and "hlky/Z-Image-Turbo-Fun-Controlnet-Union-2.1" in source
    spec = spec_section("### 1.6")
    assert "hlky/Z-Image-Turbo-Fun-Controlnet-Union-2.1@5d85f6a430fd40300f931bd1291e0c4982094859" in spec
    config = json.loads(data)
    assert config["_class_name"] == "ZImageControlNetModel" and config["control_in_dim"] == 33
    assert len(config["control_layers_places"]) == 15 and config["control_refiner_layers_places"] == [0, 1]


def test_check_config_values():
    cfg = check_config.load_config()
    assert check_config.CONFIG_PATH == ROOT / "wenart" / "vision_check" / "check.yaml"
    qwen, glm = cfg["models"]["qwen"], cfg["models"]["glm"]
    assert (qwen["slug"], qwen["server_flags"]) == ("qwen3-vl-8b", "")
    assert (glm["slug"], glm["server_flags"], glm["licence"]) == ("glm-4.6v-flash", "--reasoning-parser glm45", "MIT")
    roles = cfg["roles"]
    assert (roles["ignore_area_frac"], roles["required_area_frac"], roles["required_min_area_frac"],
            roles["required_min_visibility"]) == (0.002, 0.03, 0.01, 0.35)
    cross = cfg["crosscheck"]
    assert (cross["depth_tolerance_m"], cross["min_visible_share"], cross["min_area_frac"],
            cross["misplaced_frac_w"]) == (0.05, 0.35, 0.01, 0.05)
    assert cfg["decoy"]["fallback_types"] == ["armchair", "desk", "bookshelf", "bathtub"]
    assert cfg["targets"] == {"fa_missing_max": 0.05, "fa_extra_max": 0.10, "removal_flagged_min": 0.80,
                              "removal_confirmed_min": 0.60, "insertion_min": 0.60, "decoy_accept_max": 0.10}


def test_default_client_factory_maps_keys_to_check_yaml_ids():
    cfg = check_config.load_config()
    client = check_config.client_factory("glm", "http://127.0.0.1:9/v1")
    assert client.model == cfg["models"]["glm"]["id"] and client.base_url == "http://127.0.0.1:9/v1"
    assert callable(client.run_schema)
    assert check_config.client_factory("qwen", "http://x/v1", cfg).model == "Qwen/Qwen3-VL-8B-Instruct"
    with pytest.raises(KeyError):
        check_config.client_factory("llava", "http://x/v1")


def test_style_photo_fixture_is_a_byte_copy_of_the_m4_render():
    fixture = ROOT / "tests" / "fixtures" / "style_photo_synthetic-03_salon.jpg"
    source = ROOT / "results" / "renders" / "synthetic-03" / "cam_r_L0_salon_1_preview.jpg"
    assert fixture.read_bytes() == source.read_bytes()


# --------------------------------------------------------------------------
# Skeletons
# --------------------------------------------------------------------------

def test_skeleton_packages_import_without_torch_or_pil():
    code = ("import sys, wenart.gate, wenart.polish, wenart.polish.config, wenart.vision_check, "
            "wenart.vision_check.expected, wenart.vision_check.config, wenart.report; "
            "print(','.join(m for m in ('torch', 'transformers', 'diffusers', 'PIL', 'cv2') if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == ""


def params(fn) -> list:
    return [(p.name, p.default) for p in inspect.signature(fn).parameters.values()]


def test_gate_api_signatures():
    import wenart.gate as gate
    assert gate.Gate is gate_api.Gate and gate.decide is gate_api.decide and gate.Reference is gate_api.Reference
    E = inspect.Parameter.empty
    assert params(gate_api.Gate.__init__) == [("self", E), ("thresholds", None), ("models", None), ("device", "cuda")]
    assert params(gate_api.Gate.prepare) == [("self", E), ("view", E), ("ref_rgb", E)]
    assert params(gate_api.Gate.compare) == [("self", E), ("ref", E), ("test_rgb", E)]
    assert params(gate_api.decide) == [("metrics", E), ("thresholds", E)]
    g = gate_api.Gate(models="fake", device="cpu")
    assert g.thresholds == gate_api.load_thresholds() and g.models == "fake" and g.device == "cpu"
    assert gate_api.Gate(thresholds={"edges": {}}).thresholds == {"edges": {}}
    assert gate_api.Gate(thresholds=gate_api.THRESHOLDS_PATH).thresholds == gate_api.load_thresholds()
    ref = gate_api.Reference(view=None, rgb=None)
    assert ref.gate_key == "" and ref.model_outputs == {}
    with pytest.raises(NotImplementedError):
        g.prepare(None, None)
    with pytest.raises(NotImplementedError):
        g.compare(ref, None)
    with pytest.raises(NotImplementedError):
        gate_api.decide({}, {})


def test_expected_api_signatures():
    E = inspect.Parameter.empty
    assert params(expected.expected_view) == [("view", E), ("scene_manifest", E), ("building", E), ("cfg", None)]
    assert params(expected.expected_views) == [("project_out", E), ("render_dir", None)]
    assert params(expected.sweep_views) == [("expected_views", E), ("n", E)]
    assert params(expected.largest_required) == [("expected", E)]
    for fn, args in ((expected.expected_view, (None, {}, {})), (expected.expected_views, ("x",)),
                     (expected.sweep_views, ({}, 4)), (expected.largest_required, ({},))):
        with pytest.raises(NotImplementedError):
            fn(*args)
