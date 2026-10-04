"""CPU tests of the generated-furniture step (docs/milestone8.md §3; wenart/assets/generate.py, generate.yaml,
scripts/pod_setup_trellis.sh).

No GPU, no torch: the plan runs on canned accepted lists and catalogues; the run uses fake image and model backends
that write small PNGs and GLBs (and a fake clock for the deadline). Covered: the plan lists only the gaps (accepted
records, styles with the family or ``neutral``, beds with a mattress or a bed frame, decor and parametric entries
ignored), fixed equipment is never planned, the prompt template per type and family, deterministic seeds, the survey
record shape (the ``survey.json`` candidate fields plus the milestone 8 fields), the uid format, resuming by key and
sha256, retries of failed models, the deadline (exit 3), backend failures (exit 1), the CLI exit codes, the local
``pipeline.json`` patch, and the conventions of the setup script (bash -n, set -Eeuo pipefail, ERR trap, logs under
/workspace/logs, no secret echoed, the plan-only mode's arch list and wheel key).
"""
import ast
import json
import os
import re
import struct
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from wenart.assets import generate as G
from wenart.assets import objaverse as OV
from wenart.furniture import catalog as C

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pod_setup_trellis.sh"
CFG = G.load_config()
FIXED = ("stair", "kitchen_counter", "kitchen_island", "unknown")
UID_RE = re.compile(r"^gen_([a-z_]+?)_(scandinavian|japandi|modern_minimal|minimal|modern|industrial|mediterranean|"
                    r"classic|rustic)_(\d+)_([0-9a-f]{8})$")


def quiet(*_args, **_kwargs):
    pass


# --------------------------------------------------------------------------
# Canned files
# --------------------------------------------------------------------------

def make_glb(path: Path, triangles: int = 2000, textured: bool = True, salt: int = 0, indexed: bool = False) -> Path:
    """A small GLB 2.0 with ``triangles`` triangles (positions only, or indexed), optionally textured."""
    n_vert = 3 * triangles
    data = struct.pack(f"<{3 * n_vert}f", *([0.0] * (3 * n_vert)))
    data += struct.pack("<I", salt)                         # makes the sha256 differ per item
    data += b"\0" * (-len(data) % 4)
    accessors = [{"bufferView": 0, "componentType": 5126, "count": n_vert, "type": "VEC3",
                  "min": [0, 0, 0], "max": [1, 1, 1]}]
    prim = {"attributes": {"POSITION": 0}, "material": 0}
    views = [{"buffer": 0, "byteLength": 12 * n_vert}]
    if indexed:
        idx = struct.pack(f"<{n_vert}I", *range(n_vert))
        views.append({"buffer": 0, "byteOffset": len(data), "byteLength": len(idx)})
        data += idx
        accessors.append({"bufferView": 1, "componentType": 5125, "count": n_vert, "type": "SCALAR"})
        prim["indices"] = 1
    material = ({"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}} if textured
                else {"pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1]}})
    doc = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(data)}], "bufferViews": views,
           "accessors": accessors, "meshes": [{"primitives": [prim]}], "materials": [material],
           "nodes": [{"mesh": 0}], "scenes": [{"nodes": [0]}], "scene": 0}
    if textured:
        doc["images"] = [{"mimeType": "image/png", "bufferView": 0}]
        doc["textures"] = [{"source": 0}]
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(data)
    blob = (struct.pack("<III", 0x46546C67, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
            + struct.pack("<II", len(data), 0x004E4942) + data)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return path


def accepted_list(path: Path, records: list[dict], refused: list[dict] = ()) -> Path:
    doc = {"schema_version": "0.1", "kind": "objaverse_accepted", "accepted": records, "refused": list(refused)}
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def rec(uid, ftype, styles, accepted=True, **extra):
    return {"uid": uid, "type": ftype, "accepted": accepted, "styles": list(styles), **extra}


@pytest.fixture
def canned(tmp_path):
    """An accepted list and a catalogue: sofa scandinavian; armchair neutral; table_dining japandi (catalogue);
    a refused chair; a double bed without mattress (not counted); a single bed frame (counts); a decor rug."""
    acc = accepted_list(tmp_path / "accepted.json", [
        rec("s1", "sofa", ["scandinavian"]),
        rec("a1", "armchair", ["neutral"]),
        rec("b1", "bed_double", ["scandinavian", "japandi"], has_mattress=False),
        rec("b2", "bed_single", ["japandi"], has_mattress=False, bed_frame=True),
        rec("r1", "rug", ["scandinavian"], kind="decor"),
        rec("c0", "chair", ["scandinavian", "japandi"], accepted=False),
    ], refused=[rec("c1", "chair", ["scandinavian"], accepted=False)])
    cat = tmp_path / "catalog_library.json"
    cat.write_text(json.dumps({"entries": [
        {"id": "t1", "type": "table_dining", "styles": ["japandi"], "source": "abo"},
        {"type": "wardrobe", "parametric": True, "reason": "none"},
        {"id": "w1", "type": "wardrobe", "styles": ["scandinavian"], "kind": "decor"},
    ]}), encoding="utf-8")
    return acc, cat


def plan_of(tmp_path, catalogs, families, **kw):
    return G.make_plan(list(catalogs), families, tmp_path / "lib", CFG, log=quiet, **kw)


def pairs_of(doc) -> set:
    return {(p["type"], p["family"]) for p in doc["pairs"]}


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def test_config_covers_every_type_and_family():
    types = G.plan_types(CFG)
    assert set(CFG["exclude_types"]) == set(FIXED)
    assert set(types) == set(C.FURNITURE_TYPES) - set(FIXED)
    assert set(CFG["type_words"]) == set(types), "type_words must name every generated type"
    assert set(CFG["fixture_types"]) <= set(types)
    families = G.known_families()
    assert C.NEUTRAL not in families and families == [s for s in C.style_values() if s != C.NEUTRAL]
    for fam in families:
        hints = CFG["family_hints"][fam]
        assert hints["furniture"].strip() and hints["fixtures"].strip(), fam
    assert set(CFG["family_hints"]) == set(families)


def test_model_pins_follow_the_spec_and_the_polish():
    m = CFG["models"]
    assert m["trellis"]["repo"] == "microsoft/TRELLIS.2-4B"
    assert m["trellis"]["revision"] == "af44b45f2e35a493886929c6d786e563ec68364d"
    assert m["trellis"]["licence"] == "MIT"
    import yaml
    polish = yaml.safe_load((ROOT / "wenart" / "polish" / "polish.yaml").read_text(encoding="utf-8"))["models"]["base"]
    assert {k: m["zimage"][k] for k in ("repo", "revision", "allow_patterns")} == \
        {k: polish[k] for k in ("repo", "revision", "allow_patterns")}
    for key, spec in m.items():
        assert re.fullmatch(r"[0-9a-f]{40}", spec["revision"]), key
        assert spec["repo"].count("/") == 1 and spec.get("licence") and spec.get("allow_patterns"), key
    assert m["rembg"]["replaces"] == "briaai/RMBG-2.0" and m["rembg"]["licence"] == "MIT"
    assert m["dinov3"]["gated"] == "manual"
    assert CFG["image"] == {"size": 1024, "steps": 8, "guidance_scale": 0.0}
    t = CFG["trellis"]
    assert (t["decimation_target"], t["texture_size"], t["pipeline_type"]) == (200000, 2048, "1024_cascade")
    assert CFG["images_per_pair"] == 2


def test_module_imports_no_third_party_package_at_top_level():
    tree = ast.parse(Path(G.__file__).read_text(encoding="utf-8"))
    names = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            names += [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names.append((node.module or "").split(".")[0])
    assert names and all(n in sys.stdlib_module_names or n in ("__future__", "wenart") for n in names), names
    code = "import sys; import wenart.assets.generate as G; G.load_config(); print('torch' in sys.modules)"
    out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True, check=True)
    assert out.stdout.strip() == "False"


# --------------------------------------------------------------------------
# Plan
# --------------------------------------------------------------------------

def test_plan_lists_only_the_gaps(tmp_path, canned):
    acc, cat = canned
    doc = plan_of(tmp_path, [acc, cat], ["scandinavian", "japandi"], types=[
        "sofa", "armchair", "table_dining", "chair", "bed_double", "bed_single", "wardrobe"])
    assert pairs_of(doc) == {
        ("sofa", "japandi"), ("table_dining", "scandinavian"), ("chair", "scandinavian"), ("chair", "japandi"),
        ("bed_double", "scandinavian"), ("bed_double", "japandi"), ("bed_single", "scandinavian"),
        ("wardrobe", "scandinavian"), ("wardrobe", "japandi")}
    covered = {(c["type"], c["family"]): c["models"] for c in doc["covered"]}
    assert covered[("sofa", "scandinavian")] == ["s1"] and covered[("bed_single", "japandi")] == ["b2"]
    reasons = {p["pair"]: p["reason"] for p in doc["pairs"]}
    assert "lists 'japandi' or 'neutral'" in reasons["sofa__japandi"] and "scandinavian" in reasons["sofa__japandi"]
    assert "bed without a mattress" in reasons["bed_double__japandi"]
    chair = reasons["chair__scandinavian"]
    assert "no usable chair model" in chair and "not accepted" in chair
    assert doc["counts"] == {"pairs": 9, "covered": 5, "total": 14}
    kinds = {c["format"]: c for c in doc["catalogs"]}
    assert kinds["accepted"]["usable"] == 3 and kinds["accepted"]["skipped"] == {
        "not accepted": 1, "bed without a mattress and not a bed frame": 1}   # the rug is no furniture type
    assert kinds["catalog"]["skipped"] == {"parametric entry": 1, "decor": 1}
    assert (tmp_path / "lib" / "generate" / "plan.json").is_file()


def test_neutral_counts_for_every_family(tmp_path, canned):
    acc, _cat = canned
    doc = plan_of(tmp_path, [acc], G.known_families(), types=["armchair"])
    assert doc["pairs"] == [] and len(doc["covered"]) == len(G.known_families())


def test_plan_never_lists_fixed_equipment(tmp_path):
    empty = accepted_list(tmp_path / "accepted.json", [])
    doc = plan_of(tmp_path, [empty], ["rustic"])
    planned = {p["type"] for p in doc["pairs"]}
    assert planned == set(C.FURNITURE_TYPES) - set(FIXED)
    assert not planned & set(FIXED) and doc["excluded_types"] == list(FIXED)
    with pytest.raises(G.UsageError):
        G.parse_types("stair", CFG)
    assert G.parse_types("sofa, chair", CFG) == ["sofa", "chair"]


def test_polyhaven_catalogue_is_read_by_default(tmp_path):
    empty = accepted_list(tmp_path / "accepted.json", [])
    out = tmp_path / "lib"
    assert G.main(["plan", "--catalog", str(empty), "--families", "classic", "--out", str(out)]) == 0
    doc = json.loads((out / "generate" / "plan.json").read_text())
    assert [c["path"] for c in doc["catalogs"]][-1] == str(G.POLYHAVEN_CATALOG)
    poly = C.load(G.POLYHAVEN_CATALOG, objaverse=False)
    classic = {e["type"] for e in poly.models if C.styles_match(e, "classic") and C.has_mattress(e)}
    assert classic, "the Poly Haven catalogue has classic models"
    assert not classic & {p["type"] for p in doc["pairs"]}
    assert G.main(["plan", "--catalog", str(empty), "--families", "classic", "--out", str(out),
                   "--no-polyhaven"]) == 0
    doc = json.loads((out / "generate" / "plan.json").read_text())
    assert len(doc["catalogs"]) == 1 and classic <= {p["type"] for p in doc["pairs"]}


def test_families_are_checked(tmp_path, canned):
    acc, _cat = canned
    assert G.parse_families("japandi, modern minimal") == ["japandi", "modern minimal"]
    assert G.parse_families(["all"]) == G.known_families()
    for bad in ("baroque", "neutral", ""):
        with pytest.raises(G.UsageError):
            G.parse_families(bad)
    out = tmp_path / "lib"
    assert G.main(["plan", "--catalog", str(acc), "--families", "baroque", "--out", str(out)]) == 2
    assert G.main(["plan", "--catalog", str(tmp_path / "missing.json"), "--families", "rustic", "--out",
                   str(out)]) == 2
    (tmp_path / "bad.json").write_text("{\"foo\": 1}")
    assert G.main(["plan", "--catalog", str(tmp_path / "bad.json"), "--families", "rustic", "--out", str(out)]) == 2


def test_prompt_template_per_type_and_family():
    p = G.prompt_for("sofa", "japandi", CFG)
    assert p.startswith("a single japandi style three-seat sofa, light ash wood, black accents")
    assert p.endswith("plain white background, soft even light, no people, no text")
    assert "three-quarter front view from the left" in p and "  " not in p and "\n" not in p
    fixture = G.prompt_for("toilet", "industrial", CFG)
    assert CFG["family_hints"]["industrial"]["fixtures"] in fixture
    assert CFG["family_hints"]["industrial"]["furniture"] not in fixture
    assert G.prompt_for("bed_double", "modern minimal", CFG).startswith(
        "a single modern minimal style double bed with a headboard, a mattress")
    for ftype in G.plan_types(CFG):
        for fam in G.known_families():
            text = G.prompt_for(ftype, fam, CFG)
            assert f"a single {fam} style {CFG['type_words'][ftype]}," in text


def test_seeds_are_deterministic_and_order_free(tmp_path):
    a = G.seed_for("sofa", "japandi", 1)
    assert a == G.seed_for("sofa", "japandi", 1) and 0 <= a < 2 ** 31
    seeds = {G.seed_for(t, f, i) for t in ("sofa", "chair") for f in ("japandi", "rustic") for i in (1, 2)}
    assert len(seeds) == 8
    assert G.seed_for("sofa", "japandi", 1, base=5) == (a + 5) % 2 ** 31
    empty = accepted_list(tmp_path / "accepted.json", [])
    one = plan_of(tmp_path, [empty], ["japandi"], types=["sofa"])
    two = plan_of(tmp_path, [empty], ["rustic", "japandi"], types=["chair", "sofa"], images_per_pair=3)
    s1 = {p["pair"]: p["seeds"] for p in one["pairs"]}
    s2 = {p["pair"]: p["seeds"] for p in two["pairs"]}
    assert s1["sofa__japandi"] == [G.seed_for("sofa", "japandi", 1), G.seed_for("sofa", "japandi", 2)]
    assert s2["sofa__japandi"][:2] == s1["sofa__japandi"] and len(s2["sofa__japandi"]) == 3


def test_usable_rules():
    assert G.usable(rec("x", "sofa", ["neutral"]), "accepted") == (True, "")
    assert G.usable(rec("x", "sofa", []), "accepted")[0] is False
    assert G.usable(rec("x", "sofa", ["japandi"], accepted=False), "accepted")[0] is False
    assert G.usable({"type": "sofa", "styles": ["japandi"]}, "catalog")[0] is True
    assert G.usable(rec("x", "bed_double", ["japandi"], has_mattress=True), "accepted")[0] is True
    assert G.usable(rec("x", "bed_double", ["japandi"], bed_frame=True), "accepted")[0] is True
    assert G.usable(rec("x", "bed_double", ["japandi"]), "accepted")[0] is False


# --------------------------------------------------------------------------
# Run with fake backends
# --------------------------------------------------------------------------

class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


class FakeImages:
    """Z-Image-Turbo stand-in: a 16 x 16 image coloured by the seed; ``step`` seconds of the fake clock each."""

    def __init__(self, calls, clock=None, step=0.0, fail_load=False):
        self.calls, self.clock, self.step, self.fail_load = calls, clock, step, fail_load
        self.closed = False

    def __call__(self, cfg):          # used as the factory
        return self

    def load(self):
        if self.fail_load:
            raise RuntimeError("no CUDA device")

    def text_to_image(self, prompt, seed):
        self.calls.append(("image", prompt, seed))
        if self.clock is not None:
            self.clock.t += self.step
        img = np.full((16, 16, 3), seed % 251, dtype=np.uint8)
        img[0, 0] = len(prompt) % 256                  # a new prompt gives new pixels
        return img

    def versions(self):
        return {"fake": True}

    def close(self):
        self.closed = True


class FakeMeshes:
    """TRELLIS.2 stand-in: a GLB whose bytes depend on the seed; ``bad`` = {seed: "fail"|"untextured"}."""

    def __init__(self, calls, bad=None, clock=None, step=0.0, fail_load=False):
        self.calls, self.bad, self.clock, self.step, self.fail_load = calls, dict(bad or {}), clock, step, fail_load

    def __call__(self, cfg):
        return self

    def load(self):
        if self.fail_load:
            raise ImportError("trellis2 not installed")

    def image_to_glb(self, image_path, glb_path, seed):
        self.calls.append(("mesh", Path(image_path).name, seed))
        if self.clock is not None:
            self.clock.t += self.step
        what = self.bad.get(seed)
        if what == "fail":
            raise RuntimeError("no foreground in the image")
        make_glb(Path(glb_path), triangles=1500, textured=what != "untextured", salt=seed)
        return {"seconds_generate": 1.0}

    def versions(self):
        return {"fake": True}

    def close(self):
        pass


def small_plan(tmp_path, families=("japandi",), types=("sofa", "chair")):
    empty = accepted_list(tmp_path / "accepted.json", [])
    plan_of(tmp_path, [empty], list(families), types=list(types))
    return tmp_path / "lib" / "generate" / "plan.json"


def run(tmp_path, plan, images, meshes, **kw):
    return G.run(tmp_path / "lib", plan, cfg=kw.pop("cfg", CFG), image_backend=images, mesh_backend=meshes,
                 log=quiet, **kw)


def survey(tmp_path) -> dict:
    return json.loads((tmp_path / "lib" / G.SURVEY_NAME).read_text())


def test_run_writes_images_models_and_survey_records(tmp_path):
    plan = small_plan(tmp_path, families=("modern minimal",))
    calls = []
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    images = [c for c in calls if c[0] == "image"]
    meshes = [c for c in calls if c[0] == "mesh"]
    assert len(images) == 4 and len(meshes) == 4
    # Index-major: image 1 of every pair before image 2.
    assert [c[2] for c in images] == [G.seed_for("sofa", "modern minimal", 1), G.seed_for("chair", "modern minimal", 1),
                                      G.seed_for("sofa", "modern minimal", 2), G.seed_for("chair", "modern minimal", 2)]
    doc = survey(tmp_path)
    assert doc["kind"] == "generated_survey" and doc["complete"] is True and doc["cut_by_deadline"] is False
    cands = doc["candidates"]
    assert len(cands) == 4 and {c["group"] for c in cands} == {"sofa", "chair"}
    for c in cands:
        m = UID_RE.match(c["uid"])
        assert m and m.group(2) == "modern_minimal" and len(c["uid"]) <= 64 and OV._UID_RE.fullmatch(c["uid"])
        assert m.group(1) == c["group"] and c["glb_sha256"].startswith(m.group(4))
        assert Path(c["glb"]).is_absolute() and OV.sha256_file(Path(c["glb"])) == c["glb_sha256"]
        assert c["object_path"] == f"generate/{c['group']}__modern_minimal/model_{m.group(3)}.glb"
        assert c["face_count"] == 1500 and c["glb_info"]["textured"] is True
        assert c["source"] == "generated" and c["licence"] == "generated (TRELLIS.2-4B, MIT)"
        assert c["licence_flag"] is None and c["units_known"] is False and c["kind"] == "furniture"
        assert c["style_hint"] == "modern minimal" and c["categories"] == []
        g = c["generated"]
        assert tuple(g) == G.GENERATED_KEYS
        assert g["model"] == "microsoft/TRELLIS.2-4B" and g["revision"] == CFG["models"]["trellis"]["revision"]
        png = tmp_path / "lib" / c["generation"]["image"]
        assert OV.sha256_file(png) == g["image_sha256"]
        assert g["prompt"] == G.prompt_for(c["group"], "modern minimal", CFG)
    assert sorted(c["rank"] for c in cands if c["group"] == "sofa") == [1, 2]


def test_record_shape_equals_the_survey_shape_plus_the_new_fields(tmp_path):
    plan = small_plan(tmp_path, types=("sofa",))
    calls = []
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls), images_per_pair=1) == 0
    cand = survey(tmp_path)["candidates"][0]
    assert set(cand) == set(G.SURVEY_FIELDS) | set(G.NEW_FIELDS)
    real = ROOT / "results" / "library" / "survey.json"
    if real.is_file():                       # the Objaverse survey committed in the repo (M8: with the new fields)
        objaverse = json.loads(real.read_text())["candidates"][0]
        assert set(G.SURVEY_FIELDS) <= set(objaverse)        # every field the pipeline reads is in both
        assert set(cand) - set(objaverse) <= set(G.NEW_FIELDS)
        for key in G.SURVEY_FIELDS:
            assert type(cand[key]) is type(objaverse[key]) or cand[key] is None, key


def test_run_resumes_by_key_and_sha256(tmp_path):
    plan = small_plan(tmp_path)
    calls = []
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    first = survey(tmp_path)["candidates"]
    calls.clear()
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    assert calls == [] and survey(tmp_path)["candidates"] == first
    # A changed GLB is redone (only that model).
    victim = Path(first[0]["glb"])
    victim.write_bytes(victim.read_bytes() + b"x")
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    assert [c[0] for c in calls] == ["mesh"]
    # A changed PNG is rendered again; the same pixels come back, so its model (keyed by the image sha256) stays.
    calls.clear()
    png = tmp_path / "lib" / first[1]["generation"]["image"]
    png.write_bytes(png.read_bytes() + b"x")
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    assert [c[0] for c in calls] == ["image"]
    # A new prompt of one pair (the plan holds the prompts) redoes its images and models.
    calls.clear()
    doc = json.loads(plan.read_text())
    doc["pairs"][0]["prompt"] += ", oak"
    plan.write_text(json.dumps(doc))
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    assert [c[0] for c in calls] == ["image", "image", "mesh", "mesh"]
    assert {c[1] for c in calls if c[0] == "image"} == {doc["pairs"][0]["prompt"]}
    # Other image settings redo every image; other TRELLIS.2 settings every model; the memory mode nothing.
    calls.clear()
    cfg = dict(CFG, image=dict(CFG["image"], steps=9))
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls), cfg=cfg) == 0
    assert [c[0] for c in calls] == ["image"] * 4
    calls.clear()
    cfg = dict(cfg, trellis=dict(CFG["trellis"], texture_size=1024))
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls), cfg=cfg) == 0
    assert [c[0] for c in calls] == ["mesh"] * 4
    calls.clear()
    cfg = dict(cfg, trellis=dict(cfg["trellis"], resident_min_vram_gib=1))
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls), cfg=cfg) == 0
    assert calls == [], "the memory mode does not change the output"


def test_failed_models_are_listed_and_retried_only_on_request(tmp_path):
    plan = small_plan(tmp_path, types=("sofa",))
    bad_seed = G.seed_for("sofa", "japandi", 1)
    untex_seed = G.seed_for("sofa", "japandi", 2)
    calls = []
    meshes = FakeMeshes(calls, bad={bad_seed: "fail", untex_seed: "untextured"})
    assert run(tmp_path, plan, FakeImages(calls), meshes) == 1          # nothing usable
    doc = survey(tmp_path)
    assert doc["candidates"] == [] and doc["refused_counts"] == {"generation_failed": 1, "untextured": 1}
    assert "no foreground" in [r for r in doc["refused"] if r["code"] == "generation_failed"][0]["detail"]
    assert not list((tmp_path / "lib" / "generate" / "sofa__japandi").glob("*.tmp"))
    calls.clear()
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 1
    assert calls == []
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls), retry_failed=True) == 0
    assert [c[0] for c in calls] == ["mesh", "mesh"] and len(survey(tmp_path)["candidates"]) == 2


def test_deadline_cuts_with_exit_3_and_the_next_run_finishes(tmp_path):
    plan = small_plan(tmp_path)                       # 2 pairs x 2 images
    clock = Clock(1000.0)
    calls = []
    images = FakeImages(calls, clock=clock, step=100.0)
    code = run(tmp_path, plan, images, FakeMeshes(calls), deadline=1250.0, clock=clock)
    assert code == 3
    assert [c[0] for c in calls] == ["image", "image"]  # 1000 + 10 est., 1100 + 100 measured; 1200 + 100 > 1250
    doc = survey(tmp_path)
    assert doc["cut_by_deadline"] is True and doc["complete"] is False and doc["candidates"] == []
    assert doc["refused_counts"] == {"not_generated": 4}
    # No time to load a model: nothing starts.
    calls.clear()
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls), deadline=clock.t + 5, clock=clock) == 3
    assert calls == []
    calls.clear()
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    assert [c[0] for c in calls].count("image") == 2 and [c[0] for c in calls].count("mesh") == 4
    assert survey(tmp_path)["complete"] is True


def test_deadline_from_the_environment(tmp_path, monkeypatch):
    plan = small_plan(tmp_path, types=("sofa",))
    monkeypatch.setenv("WENART_DEADLINE", "1")
    calls = []
    assert G.main(["run", "--out", str(tmp_path / "lib"), "--plan", str(plan)], image_backend=FakeImages(calls),
                  mesh_backend=FakeMeshes(calls)) == 3
    assert calls == []
    monkeypatch.delenv("WENART_DEADLINE")
    assert G.main(["run", "--out", str(tmp_path / "lib"), "--plan", str(plan)], image_backend=FakeImages(calls),
                  mesh_backend=FakeMeshes(calls)) == 0
    assert G.main(["survey", "--out", str(tmp_path / "lib"), "--plan", str(plan)]) == 0
    assert len(survey(tmp_path)["candidates"]) == 2
    assert G.main(["run", "--out", str(tmp_path / "lib"), "--plan", str(tmp_path / "nope.json")]) == 2


def test_backend_failures_exit_1_and_keep_what_is_done(tmp_path):
    plan = small_plan(tmp_path, types=("sofa",))
    calls = []
    assert run(tmp_path, plan, FakeImages(calls, fail_load=True), FakeMeshes(calls)) == 1
    doc = survey(tmp_path)
    assert calls == [] and "Z-Image-Turbo did not load: RuntimeError: no CUDA device" in doc["errors"][0]
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls, fail_load=True)) == 1
    doc = survey(tmp_path)
    assert [c[0] for c in calls] == ["image", "image"] and "TRELLIS.2 did not load" in doc["errors"][0]
    calls.clear()
    assert run(tmp_path, plan, FakeImages(calls), FakeMeshes(calls)) == 0
    assert [c[0] for c in calls] == ["mesh", "mesh"]


def test_empty_plan_is_done(tmp_path, canned):
    acc, _cat = canned
    plan_of(tmp_path, [acc], ["scandinavian"], types=["sofa"])
    plan = tmp_path / "lib" / "generate" / "plan.json"
    assert run(tmp_path, plan, FakeImages([]), FakeMeshes([])) == 0
    assert survey(tmp_path)["candidates"] == []


def test_glb_face_count(tmp_path):
    assert G.glb_face_count(make_glb(tmp_path / "a.glb", triangles=7)) == 7
    assert G.glb_face_count(make_glb(tmp_path / "b.glb", triangles=5, indexed=True)) == 5


# --------------------------------------------------------------------------
# TRELLIS.2 pipeline.json (local snapshots)
# --------------------------------------------------------------------------

PIPELINE_JSON = {   # microsoft/TRELLIS.2-4B @af44b45 pipeline.json (samplers and normalisation left out)
    "name": "Trellis2ImageTo3DPipeline",
    "args": {
        "models": {
            "sparse_structure_decoder": "microsoft/TRELLIS-image-large/ckpts/ss_dec_conv3d_16l8_fp16",
            "sparse_structure_flow_model": "ckpts/ss_flow_img_dit_1_3B_64_bf16",
            "shape_slat_decoder": "ckpts/shape_dec_next_dc_f16c32_fp16",
            "shape_slat_flow_model_512": "ckpts/slat_flow_img2shape_dit_1_3B_512_bf16",
            "shape_slat_flow_model_1024": "ckpts/slat_flow_img2shape_dit_1_3B_1024_bf16",
            "tex_slat_decoder": "ckpts/tex_dec_next_dc_f16c32_fp16",
            "tex_slat_flow_model_512": "ckpts/slat_flow_imgshape2tex_dit_1_3B_512_bf16",
            "tex_slat_flow_model_1024": "ckpts/slat_flow_imgshape2tex_dit_1_3B_1024_bf16",
        },
        "image_cond_model": {"name": "DinoV3FeatureExtractor",
                             "args": {"model_name": "facebook/dinov3-vitl16-pretrain-lvd1689m"}},
        "rembg_model": {"name": "BiRefNet", "args": {"model_name": "briaai/RMBG-2.0"}},
        "default_pipeline_type": "1024_cascade",
    },
}


def test_pipeline_json_is_read_from_local_snapshots():
    doc, links = G.pipeline_args(PIPELINE_JSON, CFG, "/hf/dinov3", "/hf/birefnet")
    models = doc["args"]["models"]
    assert models["sparse_structure_decoder"] == "ss_decoder/ckpts/ss_dec_conv3d_16l8_fp16"
    assert models["tex_slat_decoder"] == "ckpts/tex_dec_next_dc_f16c32_fp16"
    assert links == {"ss_decoder": "ss_decoder", "ckpts": "trellis"}
    assert doc["args"]["image_cond_model"]["args"]["model_name"] == "/hf/dinov3"
    assert doc["args"]["rembg_model"]["args"]["model_name"] == "/hf/birefnet"
    assert PIPELINE_JSON["args"]["rembg_model"]["args"]["model_name"] == "briaai/RMBG-2.0", "input unchanged"
    # Every checkpoint the pipeline names is downloaded by the allow patterns of generate.yaml.
    import fnmatch
    pats = CFG["models"]["trellis"]["allow_patterns"]
    for rel in PIPELINE_JSON["args"]["models"].values():
        if rel.startswith("ckpts/"):
            for ext in (".json", ".safetensors"):
                assert any(fnmatch.fnmatch(rel + ext, p) for p in pats), rel + ext
    assert set(CFG["models"]["ss_decoder"]["files"]) == {
        "ckpts/ss_dec_conv3d_16l8_fp16.json", "ckpts/ss_dec_conv3d_16l8_fp16.safetensors"}


@pytest.mark.parametrize("path, value", [
    (("name",), "Trellis2TexturingPipeline"),
    (("args", "image_cond_model", "args", "model_name"), "facebook/dinov2-large"),
    (("args", "rembg_model", "name"), "U2Net"),
    (("args", "models", "tex_slat_decoder"), "someone/else/ckpts/x"),
])
def test_pipeline_json_with_unchecked_names_is_refused(path, value):
    doc = json.loads(json.dumps(PIPELINE_JSON))
    node = doc
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError):
        G.pipeline_args(doc, CFG, "/a", "/b")


# --------------------------------------------------------------------------
# scripts/pod_setup_trellis.sh
# --------------------------------------------------------------------------

def _script() -> str:
    return SCRIPT.read_text(encoding="utf-8")


def test_setup_script_follows_the_conventions():
    text = _script()
    assert text.startswith("#!/usr/bin/env bash\n")
    assert "set -Eeuo pipefail" in text
    assert re.search(r"^trap '[^']*' ERR$", text, re.M), "no ERR trap"
    assert os.access(SCRIPT, os.X_OK), "pod_setup_trellis.sh is not executable"
    assert subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True).returncode == 0
    assert 'WS="${WENART_WS:-/workspace}"' in text and "LOGS=$WS/logs" in text and 'mkdir -p "$LOGS"' in text
    assert 'VENV=$FAST/venv-trellis' in text and 'FAST="${WENART_FAST:-/opt/wenart}"' in text
    assert 'WHEELS_ROOT="${TRELLIS_WHEELS:-$WS/wheels/trellis}"' in text
    assert 'export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"' in text
    assert "--system-site-packages" in text and '-c "$CONSTRAINTS"' in text
    assert "setup_trellis.json" in text and 'exit 1' in text


def test_setup_script_never_prints_a_secret():
    for n, line in enumerate(_script().splitlines(), 1):
        code = line.split("#", 1)[0] if not line.lstrip().startswith("#") else ""
        assert "set -x" not in code, f"line {n}: tracing would print the environment"
        assert "RUNPOD_API_KEY" not in code, f"line {n}"
        # The shell expands the token only in the presence test; Python reads it only as a boolean.
        for _m in re.finditer(r"\$\{?HF_TOKEN\b", code):
            assert '[ -n "${HF_TOKEN:-}" ]' in code, f"line {n} expands HF_TOKEN: {line.strip()}"
        for _m in re.finditer(r"environ(\.get\(|\[)[\"']HF_TOKEN", code):
            assert 'bool(os.environ.get("HF_TOKEN"))' in code, f"line {n} reads HF_TOKEN: {line.strip()}"
        assert not re.search(r"(echo|printf|log|print)\b[^\n]*\$\{?HF_TOKEN", code), f"line {n}"
        assert "huggingface-cli login" not in code and "hf auth" not in code


def test_setup_script_pins_match_the_config_and_the_polish():
    text = _script()
    commit = re.search(r"^TRELLIS_COMMIT=([0-9a-f]{40})", text, re.M).group(1)
    assert commit == CFG["trellis_code"]["commit"]
    for name in ("NVDIFFRAST", "NVDIFFREC", "CUMESH", "FLEXGEMM"):
        assert re.search(rf"^{name}_COMMIT=[0-9a-f]{{40}}\b", text, re.M), name
    polish = (ROOT / "scripts" / "pod_setup_polish.sh").read_text(encoding="utf-8")
    for var, pkg in (("DIFFUSERS_VERSION", "diffusers"), ("TRANSFORMERS_VERSION", "transformers"),
                     ("ACCELERATE_VERSION", "accelerate"), ("HUB_VERSION", "huggingface-hub"),
                     ("OPENCV_VERSION", "opencv-python-headless")):
        version = re.search(rf"^{var}=(\S+)", polish, re.M).group(1)
        assert f'"{pkg}=={version}"' in text, (pkg, version)
    assert re.search(r'^XFORMERS_VERSION=0\.0\.33\.post2\b', text, re.M)
    assert re.search(r'^FLASH_ATTN_VERSION=2\.8\.3$', text, re.M)
    for part in ("preflight", "venv", "src", "ext", "attn", "models", "check"):
        assert re.search(rf"^part_{part}\(\) \{{", text, re.M), part


def _plan_only(tmp_path, arch=None, smi_caps="12.0"):
    fake = tmp_path / "bin"
    fake.mkdir(exist_ok=True)
    smi = fake / "nvidia-smi"
    smi.write_text(f"#!/bin/sh\nprintf '%s\\n' {smi_caps}\n", encoding="utf-8")
    smi.chmod(0o755)
    env = dict(os.environ, PATH=f"{fake}:{os.environ['PATH']}", WENART_WS=str(tmp_path / "ws"),
               WENART_FAST=str(tmp_path / "fast"), TRELLIS_SETUP_PLAN_ONLY="1")
    env.pop("TRELLIS_ARCH_LIST", None)
    if arch is not None:
        env["TRELLIS_ARCH_LIST"] = arch
    out = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    plan = dict(re.findall(r"^PLAN (\w+)=(\S*)", out.stdout, re.M))
    for line in out.stdout.splitlines():
        for k, v in re.findall(r"(\w+)=(\S+)", line):
            plan.setdefault(k, v)
    return plan, out


def test_setup_plan_only_reads_the_arch_list_from_the_gpu(tmp_path):
    plan, out = _plan_only(tmp_path)
    assert plan["arch_list"] == "12.0" and plan["arch_ok"] == "yes" and plan["fa_archs"] == "120"
    key = plan["wheel_key"]
    assert key.startswith(CFG["trellis_code"]["commit"][:8] + "-torch") and "-sm120-" in key and "." not in key
    assert plan["wheels_dir"].endswith("/ws/wheels/trellis/" + key)
    assert not (tmp_path / "fast").exists(), "plan-only changes nothing"
    plan, _ = _plan_only(tmp_path, smi_caps="8.9 8.9")
    assert plan["arch_list"] == "8.9" and "-sm89-" in plan["wheel_key"]
    plan, _ = _plan_only(tmp_path, arch="8.9;12.0")
    assert plan["fa_archs"] == "89;120" and "-sm89-sm120-" in plan["wheel_key"]
    plan, _ = _plan_only(tmp_path, arch="7.5")
    assert plan["arch_ok"] == "no"
    plan, _ = _plan_only(tmp_path, smi_caps="")
    assert plan["arch_ok"] == "no"


def test_setup_rejects_unknown_parts(tmp_path):
    env = dict(os.environ, WENART_WS=str(tmp_path / "ws"), WENART_FAST=str(tmp_path / "fast"),
               TRELLIS_SETUP_PARTS="venv build")
    out = subprocess.run(["bash", str(SCRIPT)], env=env, capture_output=True, text=True)
    assert out.returncode == 2 and "unknown part 'build'" in out.stderr
