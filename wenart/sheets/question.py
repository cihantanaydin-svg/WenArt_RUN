"""The ``sheet_region`` AI question (docs/milestone10.md §3.1 item 2, §1.5, §1.6a): crop, prompt, strict schema, the
request items and the merge of the two passes.

What: ``requests(regions, out_dir)`` renders one crop per region it is given (the stage passes only the regions
whose class neither title nor geometry decided, §3.1 item 2) (``<out>/sheets/crops/<key>.png``, 1024 px) and
returns the request items in the M7 format of ``wenart.recognition.answers`` (task ``sheet_region``);
``merge(regions, loaded, conflict, warnings)`` applies the answers of pass 1 (Qwen3-VL-8B, ``qwen``) and pass 2
(GLM-4.6V-Flash, ``glm``).

Why: AI proposes, title text and geometry decide: the passes are the last step of the fall-through, asked only
when nothing else classifies a region. An agreed class is recorded as ``unverified`` and never makes the region a
plan. (Answers given for a decided region, e.g. from an older request file, are compared: a class both passes agree
on that differs from the title or geometry is a ``region_class_disagreement`` conflict; the title or geometry wins.)

How: the schema is strict (class enum, level word, variant word, confidence, reason; no other keys) and grammar-safe
for vLLM (``wenart.recognition.schemas.grammar_problems``). The input hash is computed from a canonical description
of the crop (the region's box and entity ids, its texts, the prompt and schema), never from PNG bytes, so it is the
same in the session and on a pod with another Pillow. Temperature 0 and the seed are set by the answering client.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Callable, Optional

from wenart import building as B

TASK = "sheet_region"
CROP_VERSION = "sheet_region-1"
CROP_PX = 1024
REGION_CLASSES = ("floor_plan", "alternative_floor_plan", "furniture_plan", "section", "elevation", "roof_plan",
                  "site_plan", "detail", "3d_view", "title_block", "legend", "other")
REASON_MAX_CHARS = 160
SCHEMA: dict = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SheetRegion",
    "type": "object",
    "additionalProperties": False,
    "required": ["class", "level_word", "variant_word", "confidence", "reason"],
    "properties": {
        "class": {"enum": list(REGION_CLASSES)},
        "level_word": {"type": ["string", "null"],
                       "description": "Level words of the drawing's title as printed (ZEMİN KAT, BODRUM, 1. KAT, "
                                      "GROUND FLOOR, ATTIC), or null"},
        "variant_word": {"type": ["string", "null"],
                         "description": "Alternative or variant words of the title as printed (ALTERNATİF 2, "
                                        "(Açık mutfak), OPTION B), or null"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reason": {"type": "string", "maxLength": REASON_MAX_CHARS},
    },
}
PROMPT = (
    "The image shows one drawing region cut from an architectural CAD sheet (black lines on white, texts as "
    "drawn). Which kind of drawing is it? floor_plan = a storey seen from above with walls and room names; "
    "alternative_floor_plan = a second version of a floor plan of the same storey (its title names an "
    "alternative); furniture_plan = a floor plan titled as a furniture layout; section = a vertical cut with "
    "slabs, levels and a roof profile; elevation = an outside view of a facade; roof_plan = the roof seen from "
    "above; site_plan = the plot with the building, streets or a north arrow; detail = an enlarged construction "
    "detail; 3d_view = a perspective; title_block = the sheet's title box or table; legend = a key of symbols; "
    "other = anything else. Also give the level words and the alternative words of its title exactly as printed, "
    "or null. Report only what is visible."
)
MODEL_PASS = {"qwen": 1, "glm": 2}
EQUIVALENT = {"alternative_floor_plan": "floor_plan"}


def _same(a: Optional[str], b: Optional[str]) -> bool:
    return a is not None and b is not None and EQUIVALENT.get(a, a) == EQUIVALENT.get(b, b)


def key_of(region) -> str:
    return f"sheet_{B.slugify(region.file)}_{region.sheet.id}_{region.id}"


def canonical(region) -> dict:
    """What the crop shows and what is asked: the input of the hash."""
    return {"task": TASK, "crop_version": CROP_VERSION, "px": CROP_PX, "prompt": PROMPT,
            "schema": json.dumps(SCHEMA, sort_keys=True), "file": region.file, "sheet": region.sheet.id,
            "box": [round(float(v), 3) for v in region.box],
            "entities": sorted(e.id for e in region.ents), "texts": sorted((t.id, t.text) for t in region.texts)}


def input_sha256(region) -> str:
    blob = json.dumps(canonical(region), sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def render(region, px: int = CROP_PX):
    """The crop: the region's strokes and texts, black on white, the longer side ``px`` pixels (PIL image)."""
    from PIL import Image, ImageDraw

    from wenart.ingest.debug_image import _font

    b = region.box
    if region.texts:                                    # the crop shows the title below the drawing too
        b = (min([b[0]] + [t.box[0] for t in region.texts]), min([b[1]] + [t.box[1] for t in region.texts]),
             max([b[2]] + [t.box[2] for t in region.texts]), max([b[3]] + [t.box[3] for t in region.texts]))
    w, h = max(b[2] - b[0], 1e-9), max(b[3] - b[1], 1e-9)
    margin = 16
    scale = (px - 2 * margin) / max(w, h)
    size = (int(round(w * scale)) + 2 * margin, int(round(h * scale)) + 2 * margin)
    img = Image.new("L", size, 255)
    draw = ImageDraw.Draw(img)

    def to_px(p):
        return ((p[0] - b[0]) * scale + margin, (b[3] - p[1]) * scale + margin)

    for e in region.ents:
        for st in e.strokes:
            pts = [to_px(p) for p in st.pts]
            if len(pts) == 1 or (len(pts) == 2 and pts[0] == pts[1]):
                draw.point(pts[0], fill=0)
            elif st.fill is not None and st.closed and len(pts) >= 3:
                draw.polygon(pts, fill=96, outline=0)
            else:
                draw.line(pts + ([pts[0]] if st.closed else []), fill=0, width=1)
        if e.dim is not None:
            draw.line([to_px(e.dim.p1), to_px(e.dim.p2)], fill=0, width=1)
    for t in region.texts:
        size_px = max(6, int(round(t.height * scale * 1.2)))
        x0, y1 = to_px((t.box[0], t.box[3]))
        draw.text((x0, y1), t.text, fill=0, font=_font(size_px))
    return img


def requests(regions: list, out_dir: Path) -> list[dict]:
    """Request items (and their crop PNGs under ``out_dir/crops``) for every region."""
    items = []
    crops = Path(out_dir) / "crops"
    crops.mkdir(parents=True, exist_ok=True)
    for r in regions:
        key = key_of(r)
        rel = f"crops/{key}.png"
        render(r).save(Path(out_dir) / rel, format="PNG", optimize=False)
        items.append({"key": key, "task": TASK, "page": r.sheet.page, "images": [rel],
                      "context": {"file": r.file, "sheet": r.sheet.id, "region": r.id,
                                  "box": [round(float(v), 3) for v in r.box]},
                      "input_sha256": input_sha256(r)})
    return items


def merge(regions: list, loaded: dict, models: dict, conflict: Callable, warnings: list) -> list[str]:
    """Apply the answers (``answers.load`` output) to the regions; returns the keys without a complete pair."""
    missing = []
    for r in regions:
        key = key_of(r)
        answers = loaded.get(key) or {}
        r.ai = []
        for model_key, pass_no in MODEL_PASS.items():
            data = answers.get(model_key)
            model_id = (models.get(model_key) or {}).get("id", model_key)
            if data is None:
                r.ai.append({"pass": pass_no, "model": model_id, "class": None, "level_word": None,
                             "variant_word": None, "confidence": None, "reason": None, "error": "no answer"})
                continue
            r.ai.append({"pass": pass_no, "model": model_id, "class": data.get("class"),
                         "level_word": data.get("level_word"), "variant_word": data.get("variant_word"),
                         "confidence": data.get("confidence"), "reason": data.get("reason"), "error": None})
        classes = [a["class"] for a in r.ai]
        if any(c is None for c in classes):
            missing.append(key)
            continue
        agreed = classes[0] if _same(classes[0], classes[1]) else None
        if r.class_method in ("title", "geometry"):
            if agreed is not None and not _same(agreed, r.cls):
                cid = conflict("region_class_disagreement", [r.id],
                               f"{r.file} {r.id}: both AI passes call it {agreed}, the {r.class_method} says {r.cls}",
                               f"{r.class_method} wins")
                r.conflicts.append(cid)
            elif any(not _same(c, r.cls) for c in classes):
                warnings.append(f"{r.file} {r.id}: one AI pass calls it "
                                f"{next(c for c in classes if not _same(c, r.cls))}, the {r.class_method} says "
                                f"{r.cls} ({r.class_method} wins)")
            continue
        if agreed is not None:
            r.cls, r.class_method, r.status = agreed, "ai", "unverified"
            r.class_confidence = round(min(float(a["confidence"] or 0.0) for a in r.ai), 3)
            r.evidence.extend({"file": r.file, "page": r.sheet.page, "layer": None, "entity": None, "method": "ai",
                               "model": a["model"], "pass": a["pass"], "confidence": float(a["confidence"] or 0.0),
                               "text": a["reason"], "rule": "two_pass_agreement"} for a in r.ai)
            warnings.append(f"{r.file} {r.id}: class {agreed} from the two AI passes only: unverified, not read")
        else:
            warnings.append(f"{r.file} {r.id}: the AI passes disagree ({classes[0]} / {classes[1]}): no class")
    return missing
