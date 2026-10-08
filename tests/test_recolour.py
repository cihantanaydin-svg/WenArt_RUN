"""CPU tests of the material slots, tags and recolour support of the library models (wenart/assets/recolour.py,
docs/milestone10.md §4.5).

No GPU, no model server: a tiny GLB made in the test (two boxes, three materials, one with a texture) stands for a
library model; a fake runner writes the renders the Blender job would write (a Blender test with the real job runs
when Blender is installed: ``WENART_BLENDER``); fake judges answer per slot. Covered: the material table of a GLB, the
renamed copy, the question and its xgrammar-safe schema, the sheet, the requests, the judging through the shared
answer store, the agreement of both judges (disagreement, missing answers, mixed slots), the four catalogue fields
(thresholds, tag order, ``other`` never a tag), stale tags, and the catalogue entry.
"""
import json
import struct
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

from test_objaverse import quiet
from wenart.assets import objaverse as OV
from wenart.assets import recolour as R

CFG = R.load_config()
GLB_MAGIC = 0x46546C67


# --------------------------------------------------------------------------
# A tiny model: a seat box (grey fabric), four legs as one box (oak), a glass plate (textured, to test the flag)
# --------------------------------------------------------------------------

def box_glb(path: Path, boxes, materials, texture: bool = True) -> Path:
    """A GLB 2.0 of axis-aligned boxes (glTF Y up, metres), one primitive per box: ``boxes`` is
    ``[(min_xyz, max_xyz, material_index | None)]``; ``materials`` the glTF material dicts."""
    blob = b""
    views, accessors, prims = [], [], []
    cube = [0, 1, 3, 0, 3, 2, 4, 6, 7, 4, 7, 5, 0, 4, 5, 0, 5, 1, 2, 3, 7, 2, 7, 6, 0, 2, 6, 0, 6, 4, 1, 5, 7, 1, 7, 3]
    for lo, hi, mat in boxes:
        verts = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        pos = struct.pack("<24f", *[c for v in verts for c in v])
        idx = struct.pack("<36H", *cube)
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(pos)})
        blob += pos
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(idx)})
        blob += idx
        pa = len(accessors)
        accessors.append({"bufferView": len(views) - 2, "componentType": 5126, "count": 8, "type": "VEC3",
                          "min": [float(lo[i]) for i in range(3)], "max": [float(hi[i]) for i in range(3)]})
        accessors.append({"bufferView": len(views) - 1, "componentType": 5123, "count": 36, "type": "SCALAR"})
        prim = {"attributes": {"POSITION": pa}, "indices": pa + 1}
        if mat is not None:
            prim["material"] = mat
        prims.append(prim)
    doc = {"asset": {"version": "2.0"}, "meshes": [{"primitives": prims}], "materials": materials,
           "nodes": [{"mesh": 0}], "scenes": [{"nodes": [0]}], "scene": 0, "accessors": accessors}
    if texture:
        png = path.with_suffix(".tex.png")
        Image.fromarray((np.indices((4, 4, 3)).sum(axis=0) * 12).astype(np.uint8)).save(png)
        data = png.read_bytes()
        png.unlink()
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(data)})
        blob += data + b"\0" * (-len(data) % 4)
        doc["images"] = [{"mimeType": "image/png", "bufferView": len(views) - 1}]
        doc["textures"] = [{"source": 0}]
    doc["bufferViews"] = views
    doc["buffers"] = [{"byteLength": len(blob)}]
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(blob)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(struct.pack("<III", GLB_MAGIC, 2, total) + struct.pack("<II", len(js), 0x4E4F534A) + js
                     + struct.pack("<II", len(blob), 0x004E4942) + blob)
    return path


MATERIALS = [
    {"name": "Grey cloth", "pbrMetallicRoughness": {"baseColorFactor": [0.6, 0.6, 0.62, 1.0]}, "doubleSided": True},
    {"name": "Oak legs", "pbrMetallicRoughness": {"baseColorFactor": [0.55, 0.38, 0.2, 1.0]}, "doubleSided": True},
    {"name": "Glass plate", "pbrMetallicRoughness": {"baseColorTexture": {"index": 0}}, "doubleSided": True,
     "alphaMode": "BLEND"},
    {"name": "unused", "doubleSided": True},
]
SEAT = ((-0.5, 0.40, -0.4), (0.5, 0.55, 0.4), 0)           # 1.0 x 0.15 x 0.8 m
LEGS = ((-0.5, 0.0, -0.4), (0.5, 0.40, -0.35), 1)          # 1.0 x 0.40 x 0.05 m
PLATE = ((-0.5, 0.55, -0.4), (0.5, 0.57, 0.4), 2)          # 1.0 x 0.02 x 0.8 m


def box_area(box) -> float:
    lo, hi, _m = box
    d = [hi[i] - lo[i] for i in range(3)]
    return 2 * (d[0] * d[1] + d[0] * d[2] + d[1] * d[2])


@pytest.fixture
def glb(tmp_path):
    return box_glb(tmp_path / "model.glb", [SEAT, LEGS, PLATE], MATERIALS)


# --------------------------------------------------------------------------
# The GLB
# --------------------------------------------------------------------------

def test_glb_materials_lists_names_colours_textures_and_triangles(glb):
    info = R.glb_materials(glb)
    assert info["triangles"] == 36 and info["unmaterialed_triangles"] == 0
    by = {m["index"]: m for m in info["materials"]}
    assert by[0]["name"] == "Grey cloth" and by[0]["base_colour"] == [0.6, 0.6, 0.62, 1.0] and not by[0]["textured"]
    assert by[0]["triangles"] == 12 and by[1]["triangles"] == 12 and by[2]["triangles"] == 12
    assert by[2]["textured"] and by[2]["base_colour"] is None and by[2]["alpha_mode"] == "BLEND"
    assert by[3]["triangles"] == 0                        # a material no primitive uses is listed, not asked about
    assert by[3]["name"] == "unused"


def test_a_primitive_without_a_material_is_counted_apart(tmp_path):
    path = box_glb(tmp_path / "m.glb", [SEAT, (LEGS[0], LEGS[1], None)], MATERIALS[:1], texture=False)
    info = R.glb_materials(path)
    assert info["unmaterialed_triangles"] == 12 and info["materials"][0]["triangles"] == 12


def test_materials_are_renamed_by_index_and_the_rest_is_kept(glb, tmp_path):
    dst = tmp_path / "renamed" / "model.glb"
    assert R.rewrite_material_names(glb, dst) == 4
    info = R.glb_materials(dst)
    assert [m["name"] for m in info["materials"]] == [f"wenart_mat_{i}" for i in range(4)]
    assert [m["triangles"] for m in info["materials"]] == [12, 12, 12, 0]
    a, b = OV.glb_json(glb), OV.glb_json(dst)
    assert a["accessors"] == b["accessors"] and a["bufferViews"] == b["bufferViews"] and a["meshes"] == b["meshes"]
    blob = dst.read_bytes()
    _magic, _version, length = struct.unpack_from("<III", blob, 0)
    assert length == len(blob) and length % 4 == 0
    assert blob.endswith(glb.read_bytes()[-(len(OV.glb_json(glb)["buffers"]) and 40):])    # the binary chunk is copied
    with pytest.raises(ValueError, match="not a GLB"):
        bad = tmp_path / "bad.glb"
        bad.write_bytes(b"nope" * 8)
        R.rewrite_material_names(bad, tmp_path / "out.glb")


# --------------------------------------------------------------------------
# The question and its schema
# --------------------------------------------------------------------------

def test_schema_is_strict_and_xgrammar_safe():
    from wenart.recognition.schemas import grammar_problems
    schema = R.answer_schema([0, 2])
    assert schema["required"] == ["slot_0", "slot_2"] and set(schema["properties"]) == {"slot_0", "slot_2"}
    assert schema["additionalProperties"] is False
    assert schema["properties"]["slot_0"]["properties"]["material"]["enum"] == list(R.MATERIALS)
    assert grammar_problems(schema) == []
    good = {"slot_0": {"material": "fabric", "single_material": True},
            "slot_2": {"material": "glass", "single_material": False}}
    assert R.answer_errors(good, [0, 2]) == []
    assert R.answer_errors({"slot_0": good["slot_0"]}, [0, 2])                        # a slot missing
    assert R.answer_errors(dict(good, slot_3=good["slot_0"]), [0, 2])                 # a slot nobody asked
    assert R.answer_errors({"slot_0": {"material": "plastic", "single_material": True}, "slot_2": good["slot_2"]},
                           [0, 2])                                                    # not in the enum
    assert R.answer_errors({"slot_0": {"material": "wood"}, "slot_2": good["slot_2"]}, [0, 2])
    assert list(R.MATERIALS) == ["fabric", "wood", "metal", "glass", "rattan", "marble", "other"]
    assert {t for t in R.TAG_ORDER} == set(R.MATERIALS) - {"other"}
    assert R.TAG_ORDER == ("glass", "wood", "metal", "fabric", "rattan", "marble")    # design.material_tags enum order


def test_prompt_names_every_slot_and_every_material():
    text = R.prompt_for([{"index": 0, "name": "Grey cloth"}, {"index": 4, "name": "Oak legs"}])
    for word in ("slot_0", 'slot 4', '"Grey cloth"', '"Oak legs"', "magenta", "single_material", "Answer only with JSON"):
        assert word in text, word
    for material in R.MATERIALS:
        assert material in text, material


# --------------------------------------------------------------------------
# The library folder, the renders (fake), the sheet
# --------------------------------------------------------------------------

def make_library(tmp_path, glb, uid="abo_SOFA1", accepted=True):
    """A library folder with one candidate (``survey_abo.json``), ``thumbnails.json`` and ``accepted.json``."""
    out = tmp_path / "lib"
    sha = OV.sha256_file(glb)
    cand = {"uid": uid, "group": "sofa", "types": ["sofa"], "source": "abo", "title": "Test sofa", "glb": str(glb),
            "glb_sha256": sha, "units_known": True}
    OV.write_json(out / "survey_abo.json", {"kind": "abo_survey", "source": "abo", "candidates": [cand]})
    OV.write_json(out / OV.THUMBS_JSON, {"objects": {uid: {"uid": uid, "type": "sofa", "kind": "furniture",
                                                          "source": "abo", "status": "ready"}}})
    OV.write_json(out / OV.ACCEPTED_NAME, {"accepted": [{"uid": uid, "type": "sofa", "kind": "furniture",
                                                         "source": "abo", "accepted": True}] if accepted else []})
    return out, uid, sha


def fake_runner(boxes=(SEAT, LEGS, PLATE), hidden=(), calls=None):
    """What the Blender job writes: ``true.png``, ``mask_<index>.png`` (a white rectangle per slot, none for a hidden
    slot), ``result.json`` with the surface area per material index."""
    def run(_blender, jobs_path, _log, _timeout):
        jobs = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
        if calls is not None:
            calls.append([j["uid"] for j in jobs["objects"]])
        for job in jobs["objects"]:
            base = Path(job["dir"])
            px = int(jobs["settings"]["tile_px"])
            assert Path(job["glb"]).is_file() and R.glb_materials(Path(job["glb"]))["materials"][0]["name"] == \
                "wenart_mat_0"
            img = np.full((px, px, 3), 150, dtype=np.uint8)
            img[60:200, 40:220] = (90, 120, 200)
            Image.fromarray(img).save(base / "true.png")
            for k, i in enumerate(job["slots"]):
                mask = np.zeros((px, px), dtype=np.uint8)
                if i not in hidden:
                    mask[10 + 28 * k:28 + 28 * k, 40:220] = 255
                Image.fromarray(mask).convert("RGB").save(base / f"mask_{i}.png")
            areas = {str(b[2]): box_area(b) for b in boxes if b[2] is not None}
            OV.write_json(Path(job["result"]), {"uid": job["uid"], "glb_sha256": job["glb_sha256"], "key": job["key"],
                                                "ok": True, "area_m2": areas, "seconds": 0.1})
        return 0
    return run


def test_slots_step_selects_renders_and_composes_the_sheet(tmp_path, glb):
    out, uid, sha = make_library(tmp_path, glb)
    calls = []
    doc, rc = R.slots(out, work=tmp_path / "work", runner=fake_runner(calls=calls), blender="blender", log=quiet)
    assert rc == R.EXIT_OK and calls == [[uid]]
    rec = doc["models"][0]
    assert rec["uid"] == uid and rec["status"] == "ok" and rec["glb_sha256"] == sha
    by = {m["index"]: m for m in rec["materials"]}
    assert sorted(by) == [0, 1, 2]                                         # the unused material is not listed
    total = sum(box_area(b) for b in (SEAT, LEGS, PLATE))
    assert by[0]["share"] == pytest.approx(box_area(SEAT) / total, abs=1e-3)
    assert by[0]["name"] == "Grey cloth" and by[2]["textured"] and by[0]["pixels"] > 0
    assert all(m["asked"] for m in by.values())
    sheet = rec["sheets"][0]
    assert sheet["key"] == f"mat_{uid}" and sheet["slots"] == [0, 1, 2] and sheet["image"] == f"sheets/{uid}.jpg"
    img = Image.open(out / "recolour" / sheet["image"])
    assert img.size == (3 * 256, 2 * 256)                                  # the model + 3 slots on a 3-column grid
    assert len(sheet["pixels"]["sha256"]) == 64
    # The tint: the slot tile differs from the true tile exactly where the mask is white.
    arr = np.asarray(img.convert("RGB"), dtype=np.int32)
    true_tile, slot0 = arr[0:256, 0:256], arr[0:256, 256:512]
    assert np.abs(true_tile - slot0)[15, 100].sum() > 100 and np.abs(true_tile - slot0)[180, 100].sum() < 30
    # Run again: the renders are current (same GLB hash and settings), Blender is not called.
    calls.clear()
    R.slots(out, work=tmp_path / "work", runner=fake_runner(calls=calls), blender="blender", log=quiet)
    assert calls == []


def test_slots_not_seen_or_tiny_are_not_asked(tmp_path, glb):
    out, uid, _sha = make_library(tmp_path, glb)
    doc, _rc = R.slots(out, work=tmp_path / "w", runner=fake_runner(hidden=(1,)), blender="blender", log=quiet)
    by = {m["index"]: m for m in doc["models"][0]["materials"]}
    assert by[1]["asked"] is False and by[1]["not_asked"] == "not_visible" and by[1]["pixels"] == 0
    assert doc["models"][0]["sheets"][0]["slots"] == [0, 2]
    # A slot below min_slot_share of the surface is not asked either.
    tiny = box_glb(tmp_path / "tiny.glb", [SEAT, ((0, 0, 0), (0.01, 0.01, 0.01), 1)], MATERIALS[:2], texture=False)
    out2, uid2, _ = make_library(tmp_path / "two", tiny)
    doc2, _ = R.slots(out2, work=tmp_path / "w2", blender="blender", log=quiet,
                      runner=fake_runner(boxes=(SEAT, ((0, 0, 0), (0.01, 0.01, 0.01), 1))))
    by2 = {m["index"]: m for m in doc2["models"][0]["materials"]}
    assert by2[1]["not_asked"] == "share" and doc2["models"][0]["sheets"][0]["slots"] == [0]


def test_a_model_without_a_glb_or_a_material_gets_a_status(tmp_path, glb):
    out, uid, _sha = make_library(tmp_path, glb)
    Path(glb).unlink()
    doc, rc = R.slots(out, work=tmp_path / "w", runner=fake_runner(), blender="blender", log=quiet)
    assert doc["models"][0]["status"] == "no_glb" and rc == R.EXIT_FAIL and doc["counts"]["sheets"] == 0
    bare = box_glb(tmp_path / "bare.glb", [], [], texture=False)
    out2, _u, _ = make_library(tmp_path / "b", bare)
    doc2, _ = R.slots(out2, work=tmp_path / "w2", runner=fake_runner(), blender="blender", log=quiet)
    assert doc2["models"][0]["status"] == "no_material"
    (out / OV.ACCEPTED_NAME).unlink()
    with pytest.raises(R.UsageError, match="accept first"):
        R.slots(out, blender="blender", log=quiet)


def test_scope_ready_takes_the_thumbnail_objects(tmp_path, glb):
    out, uid, _sha = make_library(tmp_path, glb, accepted=False)
    assert R.select_models(out, scope="accepted") == []
    models = R.select_models(out, scope="ready")
    assert [m["uid"] for m in models] == [uid] and models[0]["glb"] == str(glb) and models[0]["type"] == "sofa"
    with pytest.raises(R.UsageError, match="scope"):
        R.select_models(out, scope="all")


def test_more_than_six_slots_make_a_second_sheet(tmp_path):
    boxes = [((i * 2.0, 0, 0), (i * 2.0 + 1, 0.5, 0.5), i) for i in range(8)]
    mats = [{"name": f"m{i}", "doubleSided": True, "pbrMetallicRoughness": {"baseColorFactor": [0.5, 0.5, 0.5, 1]}}
            for i in range(8)]
    path = box_glb(tmp_path / "eight.glb", boxes, mats, texture=False)
    out, uid, _ = make_library(tmp_path, path)
    doc, _rc = R.slots(out, work=tmp_path / "w", runner=fake_runner(boxes=boxes), blender="blender", log=quiet)
    sheets = doc["models"][0]["sheets"]
    assert [s["key"] for s in sheets] == [f"mat_{uid}", f"mat_{uid}_p1"] and [len(s["slots"]) for s in sheets] == [6, 2]
    assert sheets[1]["image"] == f"sheets/{uid}_p1.jpg"


# --------------------------------------------------------------------------
# Requests, judging, tags
# --------------------------------------------------------------------------

class FakeJudge:
    """Answers per slot from a table ``{model key: {slot index: (material, single)}}``."""

    def __init__(self, model: str, table: dict, seen: list):
        self.model, self.table, self.seen, self.deadline = model, table, seen, None

    def run_schema(self, images, prompt, schema, **kw):
        assert kw["task"] == R.TASK and kw["system_prompt"] == R.SYSTEM_PROMPT and Path(images[0]).is_file()
        self.seen.append((self.model, list(schema["required"])))
        data = {key: {"material": self.table[key][0], "single_material": self.table[key][1]}
                for key in schema["required"]}
        return SimpleNamespace(data=data, raw_text=json.dumps(data), error=None, attempts=1, latency_s=0.01)


def judge_both(out, tables, seen=None):
    seen = [] if seen is None else seen
    rcs = {}
    for key in ("qwen", "glm"):
        rcs[key] = R.judge(out, key, client_factory=lambda info, _s, key=key: FakeJudge(info["id"], tables[key], seen),
                           log=quiet, workers=1)
    return rcs, seen


AGREE = {"slot_0": ("fabric", True), "slot_1": ("wood", True), "slot_2": ("glass", True)}


def prepared(tmp_path, glb):
    out, uid, sha = make_library(tmp_path, glb)
    R.slots(out, work=tmp_path / "work", runner=fake_runner(), blender="blender", log=quiet)
    return out, uid, sha, R.write_requests(out)


def test_requests_hold_one_item_per_sheet_with_its_own_schema(tmp_path, glb):
    out, uid, _sha, req = prepared(tmp_path, glb)
    assert req["kind"] == "recolour_requests" and req["task"] == R.TASK and len(req["items"]) == 1
    item = req["items"][0]
    assert item["key"] == f"mat_{uid}" and item["images"] == [f"sheets/{uid}.jpg"] and item["task"] == R.TASK
    assert item["context"]["slots"] == [0, 1, 2] and item["context"]["uid"] == uid
    assert "Grey cloth" in item["prompt"] and len(item["input_sha256"]) == 64
    again = R.write_requests(out)
    assert again["items"][0]["input_sha256"] == item["input_sha256"]            # deterministic
    assert (out / "recolour" / "requests.json").is_file()


def test_both_judges_agree_and_the_tags_follow(tmp_path, glb):
    out, uid, sha, _req = prepared(tmp_path, glb)
    rcs, seen = judge_both(out, {"qwen": AGREE, "glm": AGREE})
    assert rcs == {"qwen": 0, "glm": 0} and len(seen) == 2
    st = R.status(out)
    assert st["complete"] and st["models"]["qwen"]["answered"] == 1 and st["models"]["glm"]["answered"] == 1
    doc = R.write_tags(out)
    fields = doc["models"][uid]
    total = sum(box_area(b) for b in (SEAT, LEGS, PLATE))
    assert fields["glb_sha256"] == sha
    assert fields["material_tags"] == ["glass", "wood", "fabric"]               # TAG_ORDER, every share >= 10 %
    assert fields["recolourable_fabric"] is True and fields["recolourable_wood"] is True
    rows = {r["index"]: r for r in fields["material_slots"]}
    assert rows[0]["material"] == "fabric" and rows[0]["agreed"] and rows[0]["separable"]
    assert rows[0]["share"] == pytest.approx(box_area(SEAT) / total, abs=1e-3) and rows[2]["textured"] is True
    assert rows[1]["name"] == "Oak legs" and rows[1]["base_colour"] == [0.55, 0.38, 0.2, 1.0]
    assert doc["counts"]["models"] == 1 and doc["counts"]["tags"]["glass"] == 1 and doc["unjudged"] == []
    assert R.tag_fields(out)[uid]["material_tags"] == ["glass", "wood", "fabric"]
    # Answers are reused by key and input hash: a second run asks nobody.
    seen.clear()
    judge_both(out, {"qwen": AGREE, "glm": AGREE}, seen)
    assert seen == []


def test_disagreement_mixed_slots_and_small_shares_decide_nothing(tmp_path, glb):
    out, uid, _sha, _req = prepared(tmp_path, glb)
    qwen = {"slot_0": ("fabric", True), "slot_1": ("wood", False), "slot_2": ("glass", True)}
    glm = {"slot_0": ("fabric", True), "slot_1": ("wood", True), "slot_2": ("marble", True)}
    judge_both(out, {"qwen": qwen, "glm": glm})
    fields = R.write_tags(out)["models"][uid]
    rows = {r["index"]: r for r in fields["material_slots"]}
    assert rows[1]["material"] == "wood" and rows[1]["agreed"] and not rows[1]["separable"]    # one judge: mixed
    assert rows[2]["material"] == "other" and not rows[2]["agreed"]                             # glass vs marble
    assert fields["material_tags"] == ["wood", "fabric"] and fields["recolourable_wood"] is False
    assert fields["recolourable_fabric"] is True


def test_decide_slot_and_model_tags_rules():
    both = lambda a, b: {"qwen": {"slot_0": {"material": a[0], "single_material": a[1]}},        # noqa: E731
                         "glm": {"slot_0": {"material": b[0], "single_material": b[1]}}}
    assert R.decide_slot(both(("metal", True), ("metal", True)), 0) == {
        "material": "metal", "agreed": True, "separable": True, "judges": {"qwen": "metal", "glm": "metal"}}
    assert R.decide_slot(both(("metal", True), ("metal", False)), 0)["separable"] is False
    assert R.decide_slot(both(("other", True), ("other", True)), 0)["separable"] is False       # other: nothing to recolour
    miss = R.decide_slot({"qwen": {"slot_0": {"material": "wood", "single_material": True}}, "glm": None}, 0)
    assert miss["material"] == "other" and not miss["agreed"] and "missing" in miss["note"]
    model = {"sheets": [{"key": "k", "slots": [0, 1]}],
             "materials": [{"index": 0, "name": "a", "share": 0.93, "textured": False, "base_colour": None,
                            "asked": True},
                           {"index": 1, "name": "b", "share": 0.07, "textured": True, "base_colour": None,
                            "asked": True}]}
    ans = {"k": {"qwen": {"slot_0": {"material": "fabric", "single_material": True},
                          "slot_1": {"material": "wood", "single_material": True}},
                 "glm": {"slot_0": {"material": "fabric", "single_material": True},
                         "slot_1": {"material": "wood", "single_material": True}}}}
    got = R.model_tags(model, ans, CFG)
    assert got["material_tags"] == ["fabric"]                                    # wood covers 7 % < min_tag_share 10 %
    assert got["recolourable_fabric"] is True and got["recolourable_wood"] is True   # 7 % >= min_recolour_share 5 %
    model["materials"][1]["share"] = 0.04
    assert R.model_tags(model, ans, CFG)["recolourable_wood"] is False
    ans["k"]["glm"] = None
    assert R.model_tags(model, ans, CFG) is None                                 # a missing answer: not judged


def test_unjudged_models_get_no_fields(tmp_path, glb):
    out, uid, _sha, _req = prepared(tmp_path, glb)
    doc = R.write_tags(out)                                                      # nobody answered yet
    assert doc["models"] == {} and doc["unjudged"] == [uid]
    assert R.main(["tags", "--out", str(out)]) == R.EXIT_FAIL


def test_judge_exit_codes_and_status_cli(tmp_path, glb, capsys):
    out, uid, _sha, _req = prepared(tmp_path, glb)
    rc = R.main(["judge", "--out", str(out), "--model-key", "qwen", "--deadline", "1"])
    assert rc == R.EXIT_DEADLINE                                                 # the deadline has passed
    assert R.main(["status", "--out", str(out)]) == R.EXIT_FAIL
    assert "0 answered" in capsys.readouterr().out
    assert R.main(["requests", "--out", str(tmp_path / "nowhere")]) == R.EXIT_SERVER
    assert "slots.json not found" in capsys.readouterr().err


def test_stale_answers_are_asked_again(tmp_path, glb):
    out, uid, _sha, _req = prepared(tmp_path, glb)
    judge_both(out, {"qwen": AGREE, "glm": AGREE})
    # A new sheet (the renders changed) has another input hash: the stored answers are stale.
    sheet = out / "recolour" / "sheets" / f"{uid}.jpg"
    Image.fromarray(np.full((10, 10, 3), 7, dtype=np.uint8)).save(sheet)
    R.write_requests(out)
    assert R.status(out)["models"]["qwen"]["stale"] == 1
    assert R.write_tags(out)["unjudged"] == [uid]


# --------------------------------------------------------------------------
# The catalogue
# --------------------------------------------------------------------------

def test_catalog_entry_gets_the_four_fields_and_a_generated_plant_its_species():
    cand = {"uid": "gen_plant_large_modern_1_abcd1234", "source": "generated", "licence": "generated (TRELLIS.2-4B, MIT)",
            "title": "Generated modern plant large (1)", "glb_info": {"textured": True},
            "generated": {"prompt": "p", "image_sha256": "0" * 64, "model": "m", "revision": "r", "seed": 1},
            "attributes": {"species": "palm", "pot": "rattan"}, "style_hint": "modern", "units_known": False}
    obj = {"unit": {"scale": 1.0, "note": "n", "ok": True}, "measure": {"bbox_min_raw": [0, 0, 0],
                                                                       "bbox_max_raw": [0.5, 0.5, 1.6]}}
    dec = {"type": "plant_large", "kind": "decor", "decor_type": "plant_large", "front_axis": "-Y",
           "front_axis_confidence": "low", "front_axis_note": "none", "styles": ["modern"], "style_note": "s",
           "quality": [5, 4], "licence_flag": None}
    from wenart.assets import objaverse as ov
    fields = {"material_slots": [{"index": 0, "material": "other"}], "material_tags": ["rattan"],
              "recolourable_fabric": False, "recolourable_wood": False, "glb_sha256": "x"}
    entry = ov.catalog_entry(cand, obj, dec, "f" * 64, ov.load_config(), None, fields)
    assert entry["type"] == "decor_plant_large" and entry["species"] == "palm" and entry["pot"] == "rattan"
    assert entry["material_tags"] == ["rattan"] and entry["recolourable_fabric"] is False
    assert "glb_sha256" not in entry or entry["sha256_glb"] == "f" * 64          # only the four fields are copied
    assert set(ov.MATERIAL_FIELDS) <= set(entry)
    plain = ov.catalog_entry(cand, obj, dec, "f" * 64, ov.load_config(), None)
    assert not set(ov.MATERIAL_FIELDS) & set(plain)                              # a model nobody judged: no fields


# --------------------------------------------------------------------------
# Blender (the real job), when Blender is there
# --------------------------------------------------------------------------

def _blender():
    from wenart.blender.cli import find_blender
    return find_blender()


@pytest.mark.skipif(_blender() is None, reason="no Blender binary (WENART_BLENDER)")
def test_real_blender_job_renders_masks_and_measures_areas(tmp_path, glb):
    out, uid, _sha = make_library(tmp_path, glb)
    doc, rc = R.slots(out, work=tmp_path / "work", blender=_blender(), device="cpu", log=quiet)
    assert rc == R.EXIT_OK, (tmp_path / "work" / "blender.log").read_text()[-2000:]
    rec = doc["models"][0]
    assert rec["status"] == "ok"
    by = {m["index"]: m for m in rec["materials"]}
    total = sum(box_area(b) for b in (SEAT, LEGS, PLATE))
    for box in (SEAT, LEGS, PLATE):
        m = by[box[2]]
        assert m["area_m2"] == pytest.approx(box_area(box), rel=0.01)           # world-space areas through Blender
        assert m["share"] == pytest.approx(box_area(box) / total, abs=0.01)
    assert by[0]["pixels"] > by[1]["pixels"] > 0                                 # the seat shows more than the legs
    base = tmp_path / "work" / uid
    true = np.asarray(Image.open(base / "true.png").convert("RGB"))
    assert true.shape == (256, 256, 3) and true.std() > 5                       # not an empty image
    masks = [np.asarray(Image.open(base / f"mask_{i}.png").convert("L")) > 127 for i in (0, 1, 2)]
    assert all(m.any() for m in masks)
    for a, b in ((0, 1), (0, 2), (1, 2)):                                        # a pixel belongs to one slot
        assert (masks[a] & masks[b]).sum() <= 0.05 * min(masks[a].sum(), masks[b].sum()), (a, b)
    assert Image.open(out / "recolour" / rec["sheets"][0]["image"]).size == (768, 512)
    # The renders are the same on a second run (reused), and the work folder holds a status file.
    assert json.loads((tmp_path / "work" / "blender_status.json").read_text())["done"] == [uid]
