"""Material slots, material tags and recolour support of the library models (docs/milestone10.md §4.5).

What: the brief names a fabric colour ("light grey fabric sofa"), a wood ("natural light wood furniture") and a material
("glass coffee table"). A library GLB can only take such a colour on the parts that are that material, so the library
step looks at every material slot of every accepted model, lets both vision judges name its material, and writes per
model the catalogue fields the fit and the builder read (names frozen in docs/milestone10.md, track F):

- ``material_slots``: ``[{index, name, material, materials, agreed, separable, share, textured, base_colour,
  colour_rgb}]`` (``index`` = the glTF material index; ``materials`` the materials both judges name for the slot;
  ``material`` the one when it is one of ``fabric, wood, metal, glass, rattan, marble``, ``mixed`` for several,
  ``other`` for none or ``other``; ``share`` of the model's surface; ``colour_rgb`` the median sRGB of the slot in a
  flat-lit render, so the fit can choose a model by colour when it cannot recolour one);
- ``material_tags``: the materials (schema enum of ``design.material_tags``: glass, wood, metal, fabric, rattan, marble)
  that both judges name for slots covering at least ``min_tag_share`` of the model's surface (``other`` is never a tag);
- ``recolourable_fabric`` / ``recolourable_wood``: a ``separable`` slot of that material covers at least
  ``min_recolour_share``. A model without such a slot is skipped for a colour brief and the fit takes another model. A
  model nobody judged has none of the four fields.

Why two judges and a mask: a slot's name ("Material.003") says nothing. Most library models have ONE material slot
(every ABO model and every generated model: the whole model is one texture atlas; checked on real ABO GLBs, 8 Oct
2026), so a slot is asked for the LIST of materials it holds (1 to 3 of the seven): the tags of such a model come from
that list, and it is recolourable only when the list is exactly ``fabric`` (or ``wood``). A model with several slots
(some Objaverse models) is recolourable per slot. A material counts when both judges name it for the slot (the
intersection); the slot is ``agreed`` when their lists are equal, ``separable`` when equal, a single material and not
``other``. Nothing is guessed from names.

How, in the order the prep pod runs (all steps read and write ``--out``, the library folder, ``<out>/recolour/``)::

    python -m wenart.assets.recolour slots    --out DIR [--assets DIR] [--work DIR] [--scope accepted|ready]
                                              [--types T1,T2] [--workers N] [--blender PATH] [--device auto|cpu]
                                              [--deadline T]
    python -m wenart.assets.recolour requests --out DIR
    python -m wenart.assets.recolour judge    --out DIR --model-key qwen|glm [--server URL] [--workers N] [--deadline T]
    python -m wenart.assets.recolour status   --out DIR
    python -m wenart.assets.recolour tags     --out DIR

1. ``slots``: the models are the accepted ones (``accepted.json``, the default; the catalogue then follows) or every
   ``ready`` thumbnail object (``--scope ready``: the judging can then run in the same vLLM session as the library
   judging, before ``accept``); ``--types`` keeps some types, ``--workers N`` runs N Blender processes. The GLB's
   materials are read from its JSON chunk (``glb_materials``) and renamed ``wenart_mat_<index>`` in a copy
   (``rewrite_material_names``), so Blender's materials map to glTF indexes. A Blender process (this file run as a
   script, like the thumbnails) renders each model in its own colours from two sides, once flat-lit (the colour of each
   slot) and once per slot as a white-on-black mask from the first side, and measures the surface area per slot.
   Outside Blender the sheet is composed: the model from both sides, then one tile per slot with the slot tinted
   magenta (``recolour/sheets/<uid>.jpg``, ``_p1`` for a second sheet; a model whose one slot covers the whole model
   gets the two model tiles only), and ``recolour/slots.json`` is written.
2. ``requests``: one request per sheet (``recolour/requests.json``, the recognition request shape, task
   ``library_material``) whose schema is built for that sheet: ``slot_<n>`` -> ``{materials: [1 to 3 of the seven]}``,
   xgrammar-safe, strict.
3. ``judge``: run inside the prep pod's Qwen and GLM sessions with the library judging (temperature 0, seed 0; the
   answer store and the exit codes of ``wenart.assets.objaverse.judge``: 0 done, 3 deadline, 2 server).
4. ``tags``: ``recolour/tags.json`` from both models' answers; ``wenart.assets.objaverse write-catalog`` copies the four
   fields of a model into its catalogue entry when the file is there.

Exit codes: 0 done, 1 nothing usable, 2 usage or server error, 3 cut by the deadline.

Inside Blender (``blender -b --factory-startup --python wenart/assets/recolour.py -- blender-slots <jobs.json>``) this
file runs as a plain script: its top-level imports are the standard library only and it loads the pure helpers of
``objaverse.py`` by path.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import struct
import sys
import time
from pathlib import Path
from typing import Callable, Optional

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "objaverse.yaml"
RECOLOUR_DIR = "recolour"
SLOTS_NAME = "slots.json"
REQUESTS_NAME = "requests.json"
TAGS_NAME = "tags.json"
SHEETS_DIR = "sheets"
TASK = "library_material"
MATERIALS: tuple[str, ...] = ("fabric", "wood", "metal", "glass", "rattan", "marble", "other")
MAX_MATERIALS = 3                                                    # materials named for one slot
TAG_ORDER: tuple[str, ...] = ("glass", "wood", "metal", "fabric", "rattan", "marble")      # design.material_tags enum
MODEL_KEYS: tuple[str, ...] = ("qwen", "glm")
GLB_MAGIC, CHUNK_JSON, CHUNK_BIN = 0x46546C67, 0x4E4F534A, 0x004E4942
MAT_PREFIX = "wenart_mat_"
EXIT_OK, EXIT_FAIL, EXIT_SERVER, EXIT_DEADLINE = 0, 1, 2, 3
SYSTEM_PROMPT = (
    "You judge the materials of 3D furniture models for a photoreal interior renderer and answer only with JSON that "
    "follows the given schema. Judge only what is visible in the image. When unsure, answer other."
)


class UsageError(ValueError):
    """A step run before its inputs exist, or a wrong argument (exit 2)."""


def _objaverse():
    """``wenart.assets.objaverse``: imported in the package; loaded by path inside Blender (its package ``__init__``
    needs modules Blender's Python does not have)."""
    try:
        from wenart.assets import objaverse as module
        return module
    except ImportError:
        name = "wenart_objaverse_standalone"
        if name in sys.modules:
            return sys.modules[name]
        spec = importlib.util.spec_from_file_location(name, HERE / "objaverse.py")
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module


def load_config(path: Optional[Path] = None) -> dict:
    """The ``recolour`` block of ``objaverse.yaml``."""
    return _objaverse().load_config(path)["recolour"]


# --------------------------------------------------------------------------
# GLB materials (pure: the JSON chunk only)
# --------------------------------------------------------------------------

def glb_materials(path: Path) -> dict:
    """The materials of a GLB and their use: ``{"materials": [{index, name, named, base_colour, textured, alpha_mode,
    triangles}], "unmaterialed_triangles": n, "triangles": n}``. ``name`` is the name the glTF importer of Blender gives
    the material (the file's name, or ``Material_<index>`` when the file has none: the scene builder matches slots to
    imported materials by that name); ``named`` says whether the file named it. ``base_colour`` is the
    ``baseColorFactor`` (rgba, linear) or None; ``textured`` a base colour texture; ``triangles`` counts the triangles
    of the primitives that use it."""
    doc = _objaverse().glb_json(path)
    accessors = doc.get("accessors") or []
    counts: dict[Optional[int], int] = {}
    for mesh in doc.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            ref = prim.get("indices")
            if ref is None:
                ref = (prim.get("attributes") or {}).get("POSITION")
            if ref is None or ref >= len(accessors):
                continue
            n = int(accessors[ref].get("count") or 0)
            mode = prim.get("mode", 4)
            tri = n // 3 if mode == 4 else max(n - 2, 0) if mode in (5, 6) else 0
            counts[prim.get("material")] = counts.get(prim.get("material"), 0) + tri
    materials = []
    for i, mat in enumerate(doc.get("materials") or []):
        pbr = mat.get("pbrMetallicRoughness") or {}
        factor = pbr.get("baseColorFactor")
        materials.append({"index": i, "name": str(mat.get("name") or f"Material_{i}"), "named": bool(mat.get("name")),
                          "base_colour": [round(float(v), 4) for v in factor] if factor else None,
                          "textured": isinstance(pbr.get("baseColorTexture"), dict),
                          "alpha_mode": mat.get("alphaMode") or "OPAQUE", "triangles": counts.get(i, 0)})
    return {"materials": materials, "unmaterialed_triangles": counts.get(None, 0), "triangles": sum(counts.values())}


def rewrite_material_names(src: Path, dst: Path) -> int:
    """Copy ``src`` to ``dst`` with every glTF material named ``wenart_mat_<index>`` (the Blender importer then names
    its materials by index, whatever the file called them); returns the number of materials. Other chunks stay."""
    data = Path(src).read_bytes()
    magic, version, _length = struct.unpack_from("<III", data, 0)
    if magic != GLB_MAGIC or version != 2:
        raise ValueError("not a GLB 2.0 file")
    chunks, offset = [], 12
    while offset + 8 <= len(data):
        clen, ctype = struct.unpack_from("<II", data, offset)
        chunks.append([ctype, data[offset + 8:offset + 8 + clen]])
        offset += 8 + clen
    if not chunks or chunks[0][0] != CHUNK_JSON:
        raise ValueError("first GLB chunk is not JSON")
    doc = json.loads(chunks[0][1].decode("utf-8"))
    materials = doc.get("materials") or []
    for i, mat in enumerate(materials):
        mat["name"] = f"{MAT_PREFIX}{i}"
    js = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    chunks[0][1] = js + b" " * (-len(js) % 4)
    body = b"".join(struct.pack("<II", len(blob), ctype) + blob for ctype, blob in chunks)
    Path(dst).parent.mkdir(parents=True, exist_ok=True)
    Path(dst).write_bytes(struct.pack("<III", GLB_MAGIC, 2, 12 + len(body)) + body)
    return len(materials)


# --------------------------------------------------------------------------
# The question, its schema, the answers
# --------------------------------------------------------------------------

def slot_key(index: int) -> str:
    return f"slot_{int(index)}"


def answer_schema(slots: list[int]) -> dict:
    """The strict schema of one sheet: every asked slot once, ``slot_<n>`` -> ``{materials: [1 to 3 of MATERIALS]}``.
    Only keywords xgrammar compiles (enum, array min/maxItems, objects with ``required`` and
    ``additionalProperties: false``); a repeated material is removed in code (``decide_slot``)."""
    one = {"type": "object", "additionalProperties": False, "required": ["materials"],
           "properties": {"materials": {"type": "array", "minItems": 1, "maxItems": MAX_MATERIALS,
                                        "items": {"enum": list(MATERIALS)}}}}
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "LibraryMaterials",
            "type": "object", "additionalProperties": False, "required": [slot_key(i) for i in slots],
            "properties": {slot_key(i): one for i in slots}}


def answer_errors(data, slots: list[int]) -> list[str]:
    import jsonschema
    validator = jsonschema.Draft202012Validator(answer_schema(slots))
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]


def _file_name(slot: dict, before: str, after: str = "") -> str:
    """What the question says of a slot's name: ``before`` + the quoted name + ``after`` when the file named the
    material, nothing when it did not (the importer's ``Material_<index>`` is no name the judges should read as one)."""
    if slot.get("named", True) is False:
        return ""
    return f'{before}"{slot["name"]}"{after}'


def prompt_for(slots: list[dict], whole: bool = False) -> str:
    """The question for one sheet; ``slots`` are the asked slots (``index``, ``name``). ``whole``: one slot covers the
    whole model, the sheet shows the model from two sides only."""
    if whole:
        s = slots[0]
        head = ("The image is a sheet of two renders of one 3D model from an online model library, on a plain grey "
                "background: the model in its real colours from two sides. The file has one material slot for the "
                f'whole model ({slot_key(s["index"])}{_file_name(s, ", file material name ")}): say which materials '
                "the model is made of.")
        listing = ""
    else:
        head = ("The image is a sheet of renders of one 3D model from an online model library, on a plain grey "
                'background. The first two tiles, labelled "model" and "model back", show the whole model in its real '
                "colours from two sides. Every other tile repeats the first view with ONE material slot tinted bright "
                "magenta: the magenta marks where that slot is on the model. Look at the surface under the tint in "
                "the first tile and say what it is made of.")
        listing = "Slots:\n" + "\n".join(
            f'- {slot_key(s["index"])}: the tile labelled "slot {s["index"]}"' + _file_name(s, " (file material name: ", ")")
            for s in slots)
    return "\n\n".join(part for part in [
        head, listing,
        "Fields of the answer, for every slot:\n"
        "- materials: the materials you can see in the slot, one to three, from: fabric (upholstery, cushions, linen, "
        "velvet, wool, carpet), wood (natural or painted wood, veneer, plywood), metal (steel, iron, brass, chrome, "
        "aluminium), glass (clear, tinted or frosted glass, mirror), rattan (rattan, wicker, cane, seagrass, bamboo "
        "weave), marble (marble and other stone), other (plastic, rubber, leather, ceramic, paper, concrete, anything "
        "else, or unclear). A part made of one material has one entry; list a second or third material only when it "
        "clearly occurs in the slot too (for example wooden legs and cloth in one slot).",
        "Answer only with JSON."] if part)


def _spec():
    """The judging spec of this task for ``objaverse.judge`` (same store, workers, deadline and exit codes)."""
    OV = _objaverse()

    def schema_of(item: dict) -> dict:
        return answer_schema([int(i) for i in item["context"]["slots"]])

    def valid_of(item: dict, data) -> bool:
        return data is not None and not answer_errors(data, [int(i) for i in item["context"]["slots"]])

    return OV.JudgeSpec(dir_name=RECOLOUR_DIR, task=TASK, system=SYSTEM_PROMPT, label="recolour judge",
                        answers_kind="recolour_answers", requests_kind="recolour_requests", schema_of=schema_of,
                        valid_of=valid_of)


# --------------------------------------------------------------------------
# Models to look at
# --------------------------------------------------------------------------

def select_models(out: Path, assets: Optional[Path] = None, scope: str = "accepted",
                  types: Optional[set] = None) -> list[dict]:
    """The models of the step: ``scope`` ``accepted`` (``accepted.json``) or ``ready`` (``thumbnails.json`` objects
    that are ready), each with its survey candidate's GLB (the survey cache, else ``<assets>/models/<source>/``);
    ``types`` keeps only those types (furniture type or decor type). ``[{uid, type, kind, decor_type, source, glb,
    glb_sha256}]``; a model without a readable GLB has ``glb`` None."""
    OV = _objaverse()
    out = Path(out)
    cands = {c["uid"]: c for c in OV.load_candidates(out)}
    if scope == "accepted":
        doc = OV.read_json(out / OV.ACCEPTED_NAME)
        if doc is None:
            raise UsageError(f"{out / OV.ACCEPTED_NAME} not found: run accept first (or use --scope ready)")
        picked = [d for d in doc.get("accepted") or []]
    elif scope == "ready":
        doc = OV.read_json(out / OV.THUMBS_JSON)
        if doc is None:
            raise UsageError(f"{out / OV.THUMBS_JSON} not found: run thumbnails first")
        picked = [o for _uid, o in sorted(doc.get("objects", {}).items()) if o.get("status") == "ready"]
    else:
        raise UsageError(f"scope {scope!r} is not accepted or ready")
    models = []
    for rec in picked:
        uid = rec["uid"]
        own = rec.get("decor_type") or rec.get("type") or rec.get("group")
        if types is not None and own not in types and rec.get("type") not in types:
            continue
        cand = cands.get(uid)
        glb = None
        if cand is not None:
            glb = OV.glb_source(cand, Path(assets)) if assets is not None else cand.get("glb")
            glb = glb if glb and Path(glb).is_file() else None
        models.append({"uid": uid, "type": rec.get("type") or rec.get("group"), "kind": rec.get("kind") or "furniture",
                       "decor_type": rec.get("decor_type"), "source": rec.get("source") or OV.SOURCE,
                       "glb": str(glb) if glb else None, "glb_sha256": cand.get("glb_sha256") if cand else None})
    return models


# --------------------------------------------------------------------------
# Step 1: slots (Blender renders, sheets)
# --------------------------------------------------------------------------

def model_dir(work: Path, uid: str) -> Path:
    return Path(work) / uid


def settings_key(cfg: dict) -> str:
    """What the renders depend on: the question version, the tile size, the samples and both camera angles."""
    keys = ("version", "tile_px", "samples", "mask_samples", "albedo_samples", "elevation_deg", "azimuth_deg",
            "back_azimuth_offset_deg")
    return _objaverse().canonical_sha256({k: cfg[k] for k in keys})[:16]


def job_files(job: dict) -> list[Path]:
    base = Path(job["dir"])
    return [base / "true_a.png", base / "true_b.png", base / "albedo.png"] + [base / f"mask_{i}.png"
                                                                           for i in job["slots"]]


def job_done(work: Path, job: dict, cfg: dict) -> bool:
    """The model's renders on disk are current: same GLB sha256 and settings, every render there."""
    OV = _objaverse()
    rec = OV.read_json(Path(job["result"])) if Path(job["result"]).is_file() else None
    if not rec or not rec.get("ok") or rec.get("glb_sha256") != job["glb_sha256"] or rec.get("key") != job["key"]:
        return False
    return all(f.is_file() for f in job_files(job))


def slots_jobs(models: list[dict], work: Path, cfg: dict) -> tuple[list[dict], dict]:
    """``(jobs, parsed)``: one Blender job per model with a GLB and at least one used material; ``parsed`` maps uid to
    ``glb_materials`` (models without a GLB or a material get a status in ``slots.json``)."""
    OV = _objaverse()
    jobs, parsed = [], {}
    for m in models:
        if not m["glb"]:
            continue
        try:
            info = glb_materials(Path(m["glb"]))
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            parsed[m["uid"]] = {"error": f"{type(exc).__name__}: {exc}"}
            continue
        parsed[m["uid"]] = info
        used = [x["index"] for x in info["materials"] if x["triangles"] > 0]
        if not used:
            continue
        base = model_dir(work, m["uid"])
        jobs.append({"uid": m["uid"], "glb": str(base / "model.glb"), "src": m["glb"],
                     "glb_sha256": m.get("glb_sha256") or OV.sha256_file(Path(m["glb"])), "dir": str(base),
                     "slots": used, "result": str(base / "result.json"), "key": settings_key(cfg)})
    return jobs, parsed


def mask_coverage(path: Path, threshold: float) -> tuple[int, "object"]:
    """``(pixels above the threshold, boolean array)`` of a mask render (white = the slot)."""
    import numpy as np
    from PIL import Image
    arr = np.asarray(Image.open(path).convert("L"), dtype=np.float32) / 255.0
    mask = arr > float(threshold)
    return int(mask.sum()), mask


def slot_colour(albedo_png: Path, mask_png: Path, threshold: float, min_pixels: int) -> Optional[list[int]]:
    """The median sRGB (0..255) of the flat-lit render under a slot's mask; None when the slot is seen in fewer than
    ``min_pixels`` pixels."""
    import numpy as np
    from PIL import Image
    n, mask = mask_coverage(mask_png, threshold)
    if n < int(min_pixels):
        return None
    img = np.asarray(Image.open(albedo_png).convert("RGB"), dtype=np.uint8)
    if img.shape[:2] != mask.shape:
        mask = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((img.shape[1], img.shape[0]),
                                                                              Image.NEAREST)) > 127
    return [int(v) for v in np.median(img[mask], axis=0)]


def compose_slot_sheet(true_a: Path, true_b: Path, slots: list[tuple[int, Path]], sheet_path: Path, cfg: dict) -> dict:
    """The judging sheet: the model in its own colours from two sides ("model", "model back"), then one tile per slot:
    the first view with the slot's mask tinted ``highlight_rgb`` at ``highlight_alpha`` ("slot <index>"), ``columns``
    tiles per row (no slot tiles for a model whose one slot is the whole model). Returns the sheet's
    ``pixels_sha256`` (``objaverse.pixels_sha256``)."""
    import cv2
    import numpy as np
    from PIL import Image
    OV = _objaverse()
    px, cols = int(cfg["tile_px"]), int(cfg["columns"])
    tint = np.array(cfg["highlight_rgb"], dtype=np.float32)
    alpha = float(cfg["highlight_alpha"])

    def load(path: Path):
        img = Image.open(path).convert("RGB")
        return np.asarray(img if img.size == (px, px) else img.resize((px, px), Image.LANCZOS), dtype=np.float32)
    front, back = load(true_a), load(true_b)
    tiles = [("model", front), ("model back", back)]
    for index, mask_path in slots:
        _n, mask = mask_coverage(mask_path, float(cfg["mask_threshold"]))
        if mask.shape != (px, px):
            mask = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).resize((px, px), Image.NEAREST)) > 127
        m = mask[..., None].astype(np.float32)
        tiles.append((f"slot {index}", front * (1.0 - alpha * m) + tint * (alpha * m)))
    columns = min(cols, len(tiles))
    rows = (len(tiles) + columns - 1) // columns
    sheet = np.full((rows * px, columns * px, 3), 96, dtype=np.uint8)
    for n, (label, tile) in enumerate(tiles):
        r, c = divmod(n, columns)
        sheet[r * px:(r + 1) * px, c * px:(c + 1) * px] = np.clip(tile, 0, 255).astype(np.uint8)
    sheet = np.ascontiguousarray(sheet)
    for n, (label, _tile) in enumerate(tiles):
        r, c = divmod(n, columns)
        x, y = c * px, r * px
        width = 10 * len(label) + 10
        cv2.rectangle(sheet, (x + 4, y + 4), (x + 4 + width, y + 30), (255, 255, 255), -1, cv2.LINE_8)
        cv2.putText(sheet, label, (x + 8, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_8)
    for c in range(1, columns):
        sheet[:, c * px - 1:c * px + 1] = 40
    for r in range(1, rows):
        sheet[r * px - 1:r * px + 1, :] = 40
    sheet_path = Path(sheet_path)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = sheet_path.with_name(sheet_path.name + ".tmp.jpg")
    Image.fromarray(sheet).save(tmp, format="JPEG", quality=int(cfg.get("sheet_jpeg_quality", 90)))
    tmp.replace(sheet_path)
    return OV.pixels_sha256(sheet_path)


def build_slots_doc(models: list[dict], parsed: dict, work: Path, out: Path, cfg: dict, rc: int = 0) -> dict:
    """Read the Blender results, compose the sheets and describe every model: its materials (shares, colours, which
    are asked) and its sheets. ``status`` ``ok`` or a refusal code (``no_glb``, ``glb_unreadable``, ``no_material``,
    ``not_rendered``, ``blender_error``)."""
    OV = _objaverse()
    out = Path(out)
    records = []
    for m in models:
        rec = {"uid": m["uid"], "type": m["type"], "kind": m["kind"], "decor_type": m["decor_type"],
               "source": m["source"], "glb_sha256": m["glb_sha256"], "status": "ok", "materials": [], "sheets": []}
        records.append(rec)
        info = parsed.get(m["uid"])
        if not m["glb"]:
            rec.update(status="no_glb", detail="no GLB on this pod (the survey cache or the assets cache)")
            continue
        if info is None or "error" in info:
            rec.update(status="glb_unreadable", detail=(info or {}).get("error", "not parsed"))
            continue
        if not any(x["triangles"] > 0 for x in info["materials"]):
            rec.update(status="no_material", detail="no primitive uses a material")
            continue
        base = model_dir(work, m["uid"])
        result = OV.read_json(base / "result.json")
        if not result:
            rec.update(status="not_rendered", detail=f"Blender exit {rc}" if rc else "no result written")
            continue
        if not result.get("ok"):
            rec.update(status="blender_error", detail=str(result.get("error") or "")[:300])
            continue
        areas = {int(k): float(v) for k, v in (result.get("area_m2") or {}).items() if str(k).isdigit()}
        total = sum(float(v) for v in (result.get("area_m2") or {}).values())      # faces without a material count
        tri_total = sum(x["triangles"] for x in info["materials"]) or 1
        for x in info["materials"]:
            if x["triangles"] <= 0:
                continue
            area = areas.get(x["index"])
            share = (area / total) if total > 0 and area is not None else x["triangles"] / tri_total
            mask = base / f"mask_{x['index']}.png"
            npx = mask_coverage(mask, cfg["mask_threshold"])[0] if mask.is_file() else 0
            rec["materials"].append({**{k: x[k] for k in ("index", "name", "named", "base_colour", "textured",
                                                          "alpha_mode", "triangles")},
                                     "area_m2": round(area, 5) if area is not None else None,
                                     "share": round(share, 4), "pixels": npx,
                                     "colour_rgb": slot_colour(base / "albedo.png", mask, cfg["mask_threshold"],
                                                               cfg["min_mask_pixels"]) if npx else None})
        asked = sorted((x for x in rec["materials"]
                        if x["share"] >= float(cfg["min_slot_share"]) and x["pixels"] >= int(cfg["min_mask_pixels"])),
                       key=lambda x: (-x["share"], x["index"]))
        limit = int(cfg["max_slots_per_sheet"]) * int(cfg["max_sheets_per_model"])
        asked = asked[:limit]
        asked_ids = {x["index"] for x in asked}
        for x in rec["materials"]:
            x["asked"] = x["index"] in asked_ids
            if not x["asked"]:
                x["not_asked"] = ("share" if x["share"] < float(cfg["min_slot_share"])
                                  else "not_visible" if x["pixels"] < int(cfg["min_mask_pixels"]) else "over_limit")
        # One slot that is (nearly) the whole model: the sheet shows the model from two sides and asks for its materials.
        whole = len(asked) == 1 and asked[0]["share"] >= float(cfg["whole_model_share"])
        per = int(cfg["max_slots_per_sheet"])
        order = sorted(x["index"] for x in asked)
        for part in range(0, len(order), per):
            ids = order[part:part + per]
            name = f"{m['uid']}.jpg" if part == 0 else f"{m['uid']}_p{part // per}.jpg"
            sha = compose_slot_sheet(base / "true_a.png", base / "true_b.png",
                                     [] if whole else [(i, base / f"mask_{i}.png") for i in ids],
                                     out / RECOLOUR_DIR / SHEETS_DIR / name, cfg)
            rec["sheets"].append({"key": f"mat_{m['uid']}" + ("" if part == 0 else f"_p{part // per}"),
                                  "image": f"{SHEETS_DIR}/{name}", "slots": ids, "whole": whole, "pixels": sha})
    doc = {"schema_version": OV.SCHEMA_VERSION, "kind": "recolour_slots", "generated_utc": OV.now_utc(),
           "config": cfg, "counts": {"models": len(records), "ok": sum(1 for r in records if r["status"] == "ok"),
                                     "sheets": sum(len(r["sheets"]) for r in records),
                                     "whole_model_slots": sum(1 for r in records for sh in r["sheets"] if sh["whole"])},
           "models": records}
    OV.write_json(out / RECOLOUR_DIR / SLOTS_NAME, doc)
    return doc


def slots(out: Path, assets: Optional[Path] = None, work: Optional[Path] = None, scope: str = "accepted",
          blender: Optional[str] = None, device: str = "auto", deadline: Optional[float] = None,
          runner: Optional[Callable] = None, log: Callable = print, types: Optional[set] = None,
          workers: int = 1) -> tuple[dict, int]:
    """Step 1 (module docstring) -> ``recolour/slots.json`` and the exit code. ``runner(blender, jobs_path, log_path,
    timeout) -> exit code`` replaces ``_run_blender`` (tests); ``workers`` Blender processes share the models."""
    OV = _objaverse()
    out = Path(out)
    cfg = load_config()
    work = Path(work) if work else out / OV.WORK_DIR / RECOLOUR_DIR
    models = select_models(out, assets, scope, types)
    jobs, parsed = slots_jobs(models, work, cfg)
    todo = []
    for job in jobs:
        if job_done(work, job, cfg):
            continue
        Path(job["dir"]).mkdir(parents=True, exist_ok=True)
        rewrite_material_names(Path(job["src"]), Path(job["glb"]))
        todo.append(job)
    rc = EXIT_OK
    if todo:
        s = dict(OV.load_config()["thumbnails"], **{k: cfg[k] for k in cfg})
        s["device"] = device
        if runner is None:
            if blender is None:
                from wenart.blender.cli import find_blender
                blender = find_blender()
            if blender is None:
                raise UsageError("no Blender binary: set WENART_BLENDER or pass --blender")
            runner = _run_blender
        n = max(1, min(int(workers), len(todo)))
        groups = [todo[k::n] for k in range(n)]
        paths = []
        for k, group in enumerate(groups):
            suffix = "" if n == 1 else f"_{k}"
            paths.append(OV.write_json(work / f"blender_jobs{suffix}.json", {
                "settings": s, "deadline": deadline, "work": str(work), "objects": group,
                "status": str(work / f"blender_status{suffix}.json")}))
        timeout = (deadline - time.time() + 120.0) if deadline else 3.0 * 3600.0
        log(f"recolour slots: rendering {len(todo)} model(s) of {len(models)} in {n} Blender process(es)")
        if n == 1:
            codes = [runner(blender, paths[0], work / "blender.log", timeout)]
        else:
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=n) as pool:
                codes = list(pool.map(lambda k: runner(blender, paths[k], work / f"blender_{k}.log", timeout),
                                      range(n)))
        rc = EXIT_DEADLINE if EXIT_DEADLINE in codes else max(codes)
        log(f"recolour slots: Blender exited {codes}")
    doc = build_slots_doc(models, parsed, work, out, cfg, rc)
    log(f"recolour slots: {doc['counts']} -> {out / RECOLOUR_DIR / SLOTS_NAME}")
    if rc == EXIT_DEADLINE:
        return doc, EXIT_DEADLINE
    return doc, EXIT_OK if doc["counts"]["sheets"] else EXIT_FAIL


def _run_blender(blender: str, jobs_path: Path, log_path: Path, timeout: float) -> int:
    import subprocess
    cmd = [str(blender), "-b", "--factory-startup", "--python-exit-code", "1", "--python", str(Path(__file__).resolve()),
           "--", "blender-slots", str(jobs_path)]
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with Path(log_path).open("ab") as fh:
        try:
            return subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, timeout=timeout, check=False).returncode
        except subprocess.TimeoutExpired:
            return EXIT_DEADLINE


# --------------------------------------------------------------------------
# Step 2: requests; step 3: judge (objaverse.judge with this spec); status
# --------------------------------------------------------------------------

def request_item(model: dict, sheet: dict, out: Path) -> dict:
    OV = _objaverse()
    by_index = {x["index"]: x for x in model["materials"]}
    slot_list = [{"index": i, "name": by_index.get(i, {}).get("name", f"Material_{i}"),
                  "named": by_index.get(i, {}).get("named", True)} for i in sheet["slots"]]
    whole = bool(sheet.get("whole"))
    prompt = prompt_for(slot_list, whole)
    schema = answer_schema(sheet["slots"])
    description = {"version": load_config()["version"], "task": TASK, "system": SYSTEM_PROMPT, "prompt": prompt,
                   "schema": schema, "sheet": OV.pixels_sha256(Path(out) / RECOLOUR_DIR / sheet["image"])}
    return {"key": sheet["key"], "task": TASK, "images": [sheet["image"]], "prompt": prompt,
            "context": {"uid": model["uid"], "type": model["type"], "kind": model["kind"], "slots": sheet["slots"],
                        "whole": whole, "source": model["source"]},
            "input_sha256": OV.canonical_sha256(description)}


def write_requests(out: Path) -> dict:
    """``recolour/requests.json`` for every sheet of ``slots.json``."""
    OV = _objaverse()
    out = Path(out)
    doc = OV.read_json(out / RECOLOUR_DIR / SLOTS_NAME)
    if doc is None:
        raise UsageError(f"{out / RECOLOUR_DIR / SLOTS_NAME} not found: run slots first")
    items = [request_item(m, sh, out) for m in doc["models"] if m["status"] == "ok" for sh in m["sheets"]]
    req = {"schema_version": OV.SCHEMA_VERSION, "kind": "recolour_requests", "task": TASK,
           "version": load_config()["version"], "system_prompt": SYSTEM_PROMPT, "materials": list(MATERIALS),
           "items": items}
    OV.write_json(out / RECOLOUR_DIR / REQUESTS_NAME, req)
    return req


def judge(out: Path, model_key: str, **kwargs) -> int:
    """Step 3: ``objaverse.judge`` with this task's spec."""
    return _objaverse().judge(out, model_key, spec=_spec(), **kwargs)


def status(out: Path, models: Optional[dict] = None) -> dict:
    """``{"items", "complete", "models": {key: {slug, answered, stale, failed, missing, incomplete}}}``."""
    from wenart.recognition import answers as A
    OV = _objaverse()
    spec = _spec()
    doc = OV.read_requests(out, spec)
    if doc is None:
        raise UsageError(f"{Path(out) / RECOLOUR_DIR / REQUESTS_NAME} not found: run requests first")
    items = doc.get("items") or []
    models = A.load_models() if models is None else models
    result = {"items": len(items), "models": {}}
    for key in MODEL_KEYS:
        store = OV.judge_store(out, key, models, spec)
        counts = {"answered": 0, "stale": 0, "failed": 0, "missing": 0}
        for item in items:
            counts[OV.item_state(store, item)] += 1
        result["models"][key] = {"slug": store.data["slug"], **counts, "incomplete": bool(store.data["incomplete"])}
    result["complete"] = all(m["answered"] == len(items) for m in result["models"].values())
    return result


# --------------------------------------------------------------------------
# Step 4: tags
# --------------------------------------------------------------------------

def decide_slot(answers: dict, slot: int) -> dict:
    """The materials of one slot from both models' answers (``{model_key: data | None}`` of its sheet):
    ``{"materials", "agreed", "separable", "judges"}``. A material counts when both name it (the intersection, in the
    order of ``MATERIALS``); ``agreed`` when the two lists are equal; ``separable`` when they are equal, hold one
    material and it is not ``other``. A missing answer agrees on nothing."""
    got = {}
    for key in MODEL_KEYS:
        data = answers.get(key)
        entry = (data or {}).get(slot_key(slot))
        got[key] = None if entry is None else [m for m in MATERIALS if m in set(entry["materials"])]
    judges = {k: v for k, v in got.items()}
    if any(v is None for v in got.values()):
        return {"materials": [], "agreed": False, "separable": False, "judges": judges, "note": "an answer is missing"}
    first, second = (got[k] for k in MODEL_KEYS)
    both = [m for m in MATERIALS if m in first and m in second]
    agreed = first == second
    return {"materials": both, "agreed": agreed, "separable": bool(agreed and len(both) == 1 and both[0] != "other"),
            "judges": judges}


def slot_material(materials: list[str]) -> str:
    """``material`` of a catalogue slot: the one material it holds (``other`` when that is the answer), ``mixed`` for
    several, ``other`` for none."""
    return materials[0] if len(materials) == 1 else "mixed" if materials else "other"


def model_tags(model: dict, answers_by_sheet: dict, cfg: dict) -> Optional[dict]:
    """The four catalogue fields of one model, or None when a sheet of it has no answer from both models.
    ``answers_by_sheet``: ``{sheet key: {model_key: data | None}}``."""
    decided: dict[int, dict] = {}
    for sheet in model["sheets"]:
        got = answers_by_sheet.get(sheet["key"]) or {}
        if any(got.get(k) is None for k in MODEL_KEYS):
            return None
        for i in sheet["slots"]:
            decided[i] = decide_slot(got, i)
    if not model["sheets"]:
        return None
    min_tag, min_rec = float(cfg["min_tag_share"]), float(cfg["min_recolour_share"])
    slot_rows, cover, recolour = [], {}, {"fabric": False, "wood": False}
    for x in model["materials"]:
        d = decided.get(x["index"])
        materials = d["materials"] if d else []
        row = {"index": x["index"], "name": x["name"], "material": slot_material(materials) if d else "other",
               "materials": materials, "agreed": bool(d and d["agreed"]), "separable": bool(d and d["separable"]),
               "share": x["share"], "textured": x["textured"], "base_colour": x["base_colour"],
               "colour_rgb": x.get("colour_rgb")}
        if not x.get("asked"):
            row["not_asked"] = x.get("not_asked")
        slot_rows.append(row)
        for material in materials:
            if material != "other":
                cover[material] = cover.get(material, 0.0) + float(x["share"])
        if d and d["separable"] and materials[0] in recolour and float(x["share"]) >= min_rec:
            recolour[materials[0]] = True
    tags = [t for t in TAG_ORDER if cover.get(t, 0.0) >= min_tag]
    return {"material_slots": slot_rows, "material_tags": tags, "recolourable_fabric": recolour["fabric"],
            "recolourable_wood": recolour["wood"]}


def write_tags(out: Path, models: Optional[dict] = None) -> dict:
    """``recolour/tags.json``: ``{"models": {uid: {material_slots, material_tags, recolourable_fabric,
    recolourable_wood}}, "unjudged": [uid...], "counts": ...}`` from the current, valid answers of both models."""
    from wenart.recognition import answers as A
    OV = _objaverse()
    out = Path(out)
    cfg = load_config()
    spec = _spec()
    slots_doc = OV.read_json(out / RECOLOUR_DIR / SLOTS_NAME)
    req = OV.read_requests(out, spec)
    if slots_doc is None or req is None:
        raise UsageError(f"{out / RECOLOUR_DIR}: slots.json / requests.json not found: run slots and requests first")
    models = A.load_models() if models is None else models
    stores = {k: OV.judge_store(out, k, models, spec) for k in MODEL_KEYS if k in models}
    items = {it["key"]: it for it in req["items"]}
    answers: dict[str, dict] = {}
    for key, item in items.items():
        answers[key] = {}
        for k in MODEL_KEYS:
            rec = stores[k].valid(item) if k in stores else None
            answers[key][k] = rec.get("data") if rec else None
    tagged, unjudged = {}, []
    for m in slots_doc["models"]:
        if m["status"] != "ok":
            continue
        fields = model_tags(m, {sh["key"]: answers.get(sh["key"]) for sh in m["sheets"]}, cfg)
        if fields is None:
            unjudged.append(m["uid"])
        else:
            tagged[m["uid"]] = {"glb_sha256": m["glb_sha256"], **fields}
    counts = {"models": len(tagged), "unjudged": len(unjudged),
              "recolourable_fabric": sum(1 for f in tagged.values() if f["recolourable_fabric"]),
              "recolourable_wood": sum(1 for f in tagged.values() if f["recolourable_wood"]),
              "tags": {t: sum(1 for f in tagged.values() if t in f["material_tags"]) for t in TAG_ORDER},
              "slots_not_agreed": sum(1 for f in tagged.values() for r in f["material_slots"]
                                      if not r["agreed"] and not r.get("not_asked"))}
    doc = {"schema_version": OV.SCHEMA_VERSION, "kind": "library_material_tags", "generated_utc": OV.now_utc(),
           "config": cfg, "counts": counts, "unjudged": unjudged, "models": tagged}
    OV.write_json(out / RECOLOUR_DIR / TAGS_NAME, doc)
    return doc


def tag_fields(out: Path) -> dict:
    """``{uid: the four catalogue fields}`` of ``recolour/tags.json`` (empty without it): what
    ``objaverse.write_catalog`` adds to an entry."""
    doc = _objaverse().read_json(Path(out) / RECOLOUR_DIR / TAGS_NAME)
    return dict((doc or {}).get("models") or {})


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.assets.recolour",
                                     description="material slots, material tags and recolour support of the library "
                                                 "models (docs/milestone10.md §4.5)")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--out", required=True, help="library folder ($RESULTS/library)")
        return p

    p = add("slots", "render every material slot in Blender; the sheets and slots.json")
    p.add_argument("--assets", default=None, help="assets dir (a GLB copied there by write-catalog counts)")
    p.add_argument("--work", default=None, help="renders (default <out>/work/recolour)")
    p.add_argument("--scope", default="accepted", choices=["accepted", "ready"])
    p.add_argument("--types", default=None, help="only these types, comma separated (default: every type)")
    p.add_argument("--workers", type=int, default=1, help="Blender processes sharing the models (default 1)")
    p.add_argument("--blender", default=None, help="Blender binary (default WENART_BLENDER)")
    p.add_argument("--device", default="auto", choices=["auto", "cpu"])
    p.add_argument("--deadline", type=float, default=None, help="epoch seconds (default env WENART_DEADLINE)")
    add("requests", "write recolour/requests.json")
    p = add("judge", "ask one model (inside its vLLM session)")
    p.add_argument("--model-key", required=True, help="qwen (pass 1) | glm (pass 2)")
    p.add_argument("--server", default=None)
    p.add_argument("--workers", type=int, default=None)
    p.add_argument("--deadline", type=float, default=None)
    p.add_argument("--seed-answers", default=None)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=float, default=600.0)
    p = add("status", "answered / stale / failed / missing per model")
    p.add_argument("--json", action="store_true")
    add("tags", "recolour/tags.json from both models' answers")
    return parser.parse_args(argv)


def main(argv=None, client_factory=None, runner=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["blender-slots"]:
        return _bl_slots(argv[1])
    args = parse_args(argv)
    OV = _objaverse()
    out = Path(args.out)
    try:
        if args.command == "slots":
            types = {t for t in args.types.replace(",", " ").split() if t} if args.types else None
            doc, rc = slots(out, Path(args.assets) if args.assets else None, Path(args.work) if args.work else None,
                            args.scope, args.blender, args.device, OV.deadline_of(args.deadline), runner, types=types,
                            workers=args.workers)
            print(f"recolour slots: {doc['counts']}")
            return rc
        if args.command == "requests":
            doc = write_requests(out)
            print(f"recolour requests: {len(doc['items'])} sheet(s) -> {out / RECOLOUR_DIR / REQUESTS_NAME}")
            return EXIT_OK if doc["items"] else EXIT_FAIL
        if args.command == "judge":
            return judge(out, args.model_key, server=args.server or OV.DEFAULT_SERVER, workers=args.workers,
                         deadline=args.deadline, seed_dir=args.seed_answers, client_factory=client_factory,
                         retries=args.retries, timeout_s=args.timeout)
        if args.command == "status":
            summary = status(out)
            if args.json:
                print(json.dumps(summary, indent=1))
            else:
                print(f"recolour status {out}: {summary['items']} sheet(s)")
                for key, m in summary["models"].items():
                    print(f"  {key} ({m['slug']}): {m['answered']} answered, {m['stale']} stale, {m['failed']} "
                          f"failed, {m['missing']} missing{' (incomplete)' if m['incomplete'] else ''}")
            return EXIT_OK if summary["complete"] else EXIT_FAIL
        if args.command == "tags":
            doc = write_tags(out)
            print(f"recolour tags: {doc['counts']} -> {out / RECOLOUR_DIR / TAGS_NAME}")
            return EXIT_OK if doc["models"] else EXIT_FAIL
    except (UsageError, OV.UsageError, FileNotFoundError) as exc:
        print(f"recolour {args.command}: {exc}", file=sys.stderr)
        return EXIT_SERVER
    return EXIT_FAIL


# --------------------------------------------------------------------------
# Inside Blender: renders of the model and of every slot mask
# --------------------------------------------------------------------------

def _mat_index(material) -> Optional[int]:
    """The glTF material index of a Blender material named ``wenart_mat_<index>`` (a ``.001`` suffix allowed)."""
    if material is None:
        return None
    name = str(material.name)
    if not name.startswith(MAT_PREFIX):
        return None
    digits = name[len(MAT_PREFIX):].split(".")[0]
    return int(digits) if digits.isdigit() else None


def _mask_material(bpy, name: str, value: float):
    """An emission-only material (white or black), independent of the lights."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    for node in list(tree.nodes):
        tree.nodes.remove(node)
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    emit = tree.nodes.new("ShaderNodeEmission")
    emit.inputs["Color"].default_value = (value, value, value, 1.0)
    emit.inputs["Strength"].default_value = 1.0
    tree.links.new(emit.outputs["Emission"], out.inputs["Surface"])
    return mat


def _bl_one(bpy, Vector, OV, scene, cam, sun, white, black, job: dict, s: dict) -> dict:
    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=job["glb"], import_shading="NORMALS", import_scene_as_collection=False,
                              import_select_created_objects=False)
    new = [o for o in bpy.data.objects if o.name not in before]
    meshes = [o for o in new if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("no mesh objects in the GLB")
    for ob in new:
        if ob.type == "LIGHT":
            ob.hide_render = True
    bpy.context.view_layer.update()
    areas: dict[str, float] = {}
    points = []
    for ob in meshes:
        mw = ob.matrix_world
        me = ob.data
        wv = [tuple(mw @ v.co) for v in me.vertices]
        points.extend(wv)
        for poly in me.polygons:
            slot = ob.material_slots[poly.material_index] if poly.material_index < len(ob.material_slots) else None
            idx = _mat_index(slot.material if slot is not None else None)
            _normal, area = OV.newell([wv[i] for i in poly.vertices])
            areas[str(idx)] = areas.get(str(idx), 0.0) + area
    if not points:
        raise RuntimeError("no vertices in the GLB")
    mins, maxs = OV.bounds(points)
    extents = [maxs[i] - mins[i] for i in range(3)]
    centre = [(mins[i] + maxs[i]) / 2.0 for i in range(3)]
    dist = OV.camera_distance(extents, float(s["lens_mm"]), float(s["sensor_mm"]), float(s["margin"]))
    cam.data.clip_start = max(1e-4, dist * 0.01)
    cam.data.clip_end = dist * 10.0
    base = Path(job["dir"])

    def aim(azimuth: float) -> None:
        d = OV.view_direction("-Y", float(s["elevation_deg"]), azimuth)
        loc = tuple(centre[i] + dist * d[i] for i in range(3))
        cam.location = loc
        cam.rotation_euler = (Vector(centre) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        light = OV.view_direction("-Y", float(s["sun_elevation_deg"]), azimuth + float(s["sun_azimuth_offset_deg"]))
        sun.rotation_euler = (-Vector(light)).to_track_quat("-Z", "Y").to_euler()

    def render(name: str) -> None:
        scene.render.filepath = str(base / name)
        bpy.ops.render.render(write_still=True)
    front = float(s["azimuth_deg"])
    # 1. the model in its own colours, from the first side and from the opposite one
    scene.cycles.samples = int(s["samples"])
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "AgX"
    aim(front)
    render("true_a.png")
    aim(front + float(s["back_azimuth_offset_deg"]))
    render("true_b.png")
    aim(front)
    slots_ = [(slot, slot.material) for ob in meshes for slot in ob.material_slots]
    world_bg = next((n for n in scene.world.node_tree.nodes if n.type == "BACKGROUND"), None)
    world_was = ((tuple(world_bg.inputs["Color"].default_value), world_bg.inputs["Strength"].default_value)
                 if world_bg is not None else None)
    sun_energy = sun.data.energy
    try:
        # 2. flat-lit: a white world and no sun, no tone curve: the colour of each slot (about its albedo)
        if world_bg is not None:
            world_bg.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
            world_bg.inputs["Strength"].default_value = 1.0
        sun.data.energy = 0.0
        scene.view_settings.view_transform = "Standard"
        scene.cycles.samples = int(s["albedo_samples"])
        scene.cycles.use_denoising = False
        render("albedo.png")
        # 3. one flat mask per slot: white emission on the slot, black everywhere else, no lights
        if world_bg is not None:
            world_bg.inputs["Strength"].default_value = 0.0
        scene.cycles.samples = int(s["mask_samples"])
        for index in job["slots"]:
            for slot, mat in slots_:
                slot.material = white if _mat_index(mat) == index else black
            render(f"mask_{index}.png")
    finally:
        for slot, mat in slots_:
            slot.material = mat
        if world_bg is not None:
            world_bg.inputs["Color"].default_value = world_was[0]
            world_bg.inputs["Strength"].default_value = world_was[1]
        sun.data.energy = sun_energy
        scene.view_settings.view_transform = "AgX"
    return {"area_m2": areas, "bbox_min": list(mins), "bbox_max": list(maxs), "triangles": sum(
        max(0, len(p.vertices) - 2) for ob in meshes for p in ob.data.polygons), "mesh_objects": len(meshes)}


def _bl_slots(jobs_path: str) -> int:
    """Render every job of ``blender_jobs.json``: ``true.png`` and ``mask_<index>.png`` per model and its
    ``result.json`` (areas per material index). Returns 3 when the deadline left models undone, else 0."""
    import bpy
    from mathutils import Vector

    OV = _objaverse()
    jobs = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    s = jobs["settings"]
    deadline = jobs.get("deadline")
    work = Path(jobs["work"])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    device = OV._bl_device(scene, s.get("device", "auto"))
    scene.render.resolution_x = scene.render.resolution_y = int(s["tile_px"])
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    OV._bl_world(scene, float(s["background"]))
    cam_data = bpy.data.cameras.new("slot_cam")
    cam_data.lens = float(s["lens_mm"])
    cam_data.sensor_width = float(s["sensor_mm"])
    cam_data.sensor_fit = "AUTO"
    cam = bpy.data.objects.new("slot_cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    sun_data = bpy.data.lights.new("slot_sun", "SUN")
    sun_data.energy = float(s["sun_energy"])
    sun_data.angle = math.radians(5.0)
    sun = bpy.data.objects.new("slot_sun", sun_data)
    scene.collection.objects.link(sun)
    white, black = _mask_material(bpy, "wenart_mask_white", 1.0), _mask_material(bpy, "wenart_mask_black", 0.0)
    white.use_fake_user = black.use_fake_user = True          # the orphan purge after each model must keep them
    keep = {o.name for o in bpy.data.objects}
    status_doc = {"device": device, "blender": bpy.app.version_string, "done": [], "failed": [], "left": []}
    status_path = Path(jobs.get("status") or work / "blender_status.json")
    for job in jobs["objects"]:
        if deadline and time.time() >= float(deadline):
            status_doc["left"].append(job["uid"])
            continue
        t0 = time.time()
        rec = {"uid": job["uid"], "glb_sha256": job["glb_sha256"], "key": job["key"], "ok": False, "device": device}
        try:
            rec.update(_bl_one(bpy, Vector, OV, scene, cam, sun, white, black, job, s))
            rec["ok"] = True
            status_doc["done"].append(job["uid"])
        except Exception as exc:  # noqa: BLE001 - one broken GLB must not stop the others
            rec["error"] = f"{type(exc).__name__}: {exc}"
            status_doc["failed"].append(job["uid"])
        finally:
            OV._bl_clear(bpy, keep)
            for mat in [m for m in bpy.data.materials if m.name.startswith(MAT_PREFIX) and m.users == 0]:
                bpy.data.materials.remove(mat)
        rec["seconds"] = round(time.time() - t0, 2)
        OV.write_json(Path(job["result"]), rec)
        print(f"SLOTS {job['uid']} {'ok' if rec['ok'] else rec['error']} {rec['seconds']} s", flush=True)
    status_doc["incomplete"] = bool(status_doc["left"])
    OV.write_json(status_path, status_doc)
    return EXIT_DEADLINE if status_doc["left"] else EXIT_OK


if __name__ == "__main__":
    # Inside Blender the arguments follow "--"; as ``python -m`` they are the usual ones.
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]))
