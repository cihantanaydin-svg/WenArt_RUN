"""The audit's vision question (docs/milestone12.md §6.1 "vision check", pod P3).

What: one question per model to a vLLM server: the audit sheet (``render.py``: the four views with the person, the
seat bar and the grid, the dimensions printed), the title, the type and the size in the text. The answer
(``SCHEMA``, strict JSON, temperature 0, seed 0) says: is it this type (else what), one object, a real manufactured
product, indoor or outdoor, upright, the size plausible next to the scale reference, a drawer or door open, the
styles, the photoreal quality 1-5 with anchored descriptions, where its front is, bedding / cushions / pillows (beds
and seats) and the decor contact (flat bottom, hangs, leans, drapes).

Pass 2 (``SCHEMA2``): only where code cannot confirm the type (no title evidence: generated models and titles that
name no type, ``decide.py``) and pass 1 says it is the type: an independent question that only asks which type it
is, from the types of its kind (CLAUDE.md: two independent passes stay only where no code check exists).

Why: the M8-M10 judges saw no scale, no title and no size; they accepted an air bed, a corpse and street lamps.

How: the requests (``ask/requests.json``, ``ask/requests2.json``) hash the question, the schema and the sheet's
pixels (``input_sha256``); the answers live in the recognition answer store format (``ask/answers_<slug>.json``,
``ask/answers2_<slug>.json``) and are reused while current. The model is a key of
``wenart/vision_check/check.yaml`` (``audit.yaml ask.model_key``, the bake-off's pick; ``--model-key``); the worker
pool, the deadline and the exit codes are ``wenart.assets.objaverse.judge_ask``'s. ``--serve`` starts and stops the
vLLM server itself (``wenart.run.servers.server``).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.audit import EXIT_DEADLINE, EXIT_NOTHING, EXIT_OK, EXIT_SERVER
from wenart.assets.audit.items import has_front

ASK_DIR = "ask"
TASK = "library_audit"
TASK2 = "library_audit_type"
SYSTEM = ("You audit 3D models for a photoreal interior renderer and answer only with JSON that follows the given "
          "schema. Judge only what is visible in the image and the facts given in the text. When unsure, answer "
          "false, null or 'unclear'.")
QUALITY_ANCHORS = ("5 = could pass for a product photo: detailed shape, real materials, clean geometry; "
                   "4 = good: real proportions and materials, small flaws; "
                   "3 = plain or game-like: simple shapes, flat or repeated textures; "
                   "2 = crude: blocky or low-poly, blurry or stretched textures, wrong proportions; "
                   "1 = broken, untextured, a cartoon or a toy")
CONTACTS = ("flat_bottom", "hangs", "leans", "drapes")
FRONT_SIDES = ("front", "back", "left", "right", "none", "unclear")


def kind_types(kind: str) -> list[str]:
    from wenart.furniture import catalog as C
    if kind == "decor":
        return list(C.DECOR_TYPES)
    return [t for t in C.FURNITURE_TYPES if t not in ("unknown", "stair", "kitchen_counter", "kitchen_island",
                                                      "wall_cabinet")]


def type_words(ftype: str, kind: str) -> tuple[str, str]:
    from wenart.assets import objaverse as OV
    if kind == "decor":
        name, what, _ = OV.DECOR_WORDS.get(ftype, (ftype.replace("_", " "), ftype.replace("_", " "), ""))
        return name, what
    return OV.TYPE_WORDS.get(ftype, (ftype.replace("_", " "), ftype.replace("_", " ")))


def schema(kind: str) -> dict:
    """Pass 1 schema (strict; nullable fields answer null where they do not apply)."""
    from wenart.furniture import catalog as C
    styles = list(C.style_values())
    props = {
        "is_type": {"type": "boolean"},
        "type_guess": {"enum": kind_types(kind) + ["other"]},
        "single_object": {"type": "boolean"},
        "real_product": {"type": "boolean"},
        "indoor": {"enum": ["indoor", "outdoor", "both"]},
        "upright": {"type": "boolean"},
        "size_plausible": {"type": "boolean"},
        "parts_open": {"type": "boolean"},
        "styles": {"type": "array", "items": {"enum": styles}, "maxItems": len(styles)},
        "quality": {"type": "integer", "minimum": 1, "maximum": 5},
        "front_shown": {"enum": list(FRONT_SIDES)},
        "has_bedding": {"type": ["boolean", "null"]},
        "has_pillows": {"type": ["boolean", "null"]},
        "has_cushions": {"type": ["boolean", "null"]},
        "contact": {"enum": list(CONTACTS) + [None]},
    }
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "LibraryAudit", "type": "object",
            "additionalProperties": False, "required": list(props), "properties": props}


def schema2(kind: str) -> dict:
    """Pass 2 schema: the type only."""
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "LibraryAuditType", "type": "object",
            "additionalProperties": False, "required": ["type_guess"],
            "properties": {"type_guess": {"enum": kind_types(kind) + ["other"]}}}


def _fmt(box) -> str:
    return " x ".join(f"{float(v):.2f}" for v in box)


def prompt(item: dict, box) -> str:
    """The pass 1 question of one model (the same text for every model of a type but the facts)."""
    name, what = type_words(item["type"], item["kind"])
    types = ", ".join(kind_types(item["kind"]))
    bed = item["type"] in ("bed_single", "bed_double", "bunk_bed", "crib")
    seat = item["type"] in ("sofa", "sofa_corner", "armchair", "chaise", "chair", "bench", "ottoman", "office_chair",
                            "bar_stool")
    fields = [
        f"- is_type: true when it is a {name} ({what}).",
        f"- type_guess: what it is, from: {types}; 'other' when none fits.",
        "- single_object: true when the model is one piece (a pair of curtains or a stack of books counts as one), "
        "with nothing else (no second piece, room, person or text); the grey floor, the grid, the blue person and the "
        "orange bar are the scale reference, not part of the model.",
        "- real_product: true when it looks like a real manufactured product you could buy, not a toy, a game prop, "
        "a sculpture of a piece or an invented object.",
        "- indoor: indoor, outdoor (garden, street or park furniture) or both.",
        "- upright: true when it stands the right way up on the floor grid.",
        "- size_plausible: true when its size next to the 1.75 m person, the 0.45 m seat bar and the grid fits a real "
        f"{name}.",
        "- parts_open: true when a drawer, door or lid is open or pulled out, or a part floats apart from the rest.",
        "- styles: the interior styles it fits (an empty list when none clearly fits).",
        f"- quality: how real it would look in a photoreal interior render: {QUALITY_ANCHORS}.",
        ("- front_shown: where its front (the side people use) faces in tile 0: 'front' toward the camera, 'back' "
         "away from it, 'left' or 'right' toward that side of the image; 'unclear' when you cannot tell"
         if has_front(item["type"]) else "- front_shown: 'none' (this type has no front)."),
        ("- has_bedding: true when the bed has sheets, a duvet or a cover; has_pillows: true when it has bed "
         "pillows" if bed else "- has_bedding: null; has_pillows: null."),
        ("- has_cushions: true when it has loose or scatter cushions" if (bed or seat)
         else "- has_cushions: null."),
        ("- contact: how it rests: flat_bottom (stands on a surface), hangs (on a wall or from a ceiling), leans "
         "(against a back or a wall), drapes (lies over a host like a throw)" if item["kind"] == "decor"
         else "- contact: null."),
    ]
    return "\n\n".join([
        "The image shows one 3D model from our furniture library at its real scale: a header with its id, type, "
        "source, licence, size and title, then four renders: 0 front 3/4, 1 side (from its right), 2 top, 3 back. "
        "A grey floor with a metric grid, a 1.75 m person silhouette (blue) and a 0.45 m seat-height bar (orange) "
        "stand next to it for scale (small items get the bar and a 0.1 m grid only).",
        f"It is filed as a {name} ({what}). Its title: \"{item.get('title') or '-'}\". Its size: {_fmt(box)} m "
        "(width along its front x depth x height).",
        "Fields of the answer:\n" + "\n".join(fields),
        "Answer only with JSON.",
    ])


def prompt2(item: dict) -> str:
    types = ", ".join(kind_types(item["kind"]))
    return "\n\n".join([
        "The image shows one 3D model at its real scale: four renders (front 3/4, side, top, back) next to a 1.75 m "
        "person silhouette and a 0.45 m seat-height bar on a metric grid.",
        f"Which one of these is it? {types}. Answer 'other' when none fits.",
        "Answer only with JSON: {\"type_guess\": ...}.",
    ])


def _sha(description) -> str:
    return hashlib.sha256(json.dumps(description, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def request_item(item: dict, sheet_rel: str, sheet_px: str, box, version: str, second: bool = False) -> dict:
    p = prompt2(item) if second else prompt(item, box)
    sch = schema2(item["kind"]) if second else schema(item["kind"])
    task = TASK2 if second else TASK
    desc = {"version": version, "task": task, "system": SYSTEM, "prompt": p, "schema": sch, "sheet": sheet_px}
    return {"key": f"audit_{item['id']}", "task": task, "images": [sheet_rel], "prompt": p,
            "context": {"id": item["id"], "type": item["type"], "kind": item["kind"], "pass": 2 if second else 1},
            "input_sha256": _sha(desc)}


def build_requests(items: list[dict], measure_doc: dict, audit: Path, version: str, only: Optional[set] = None,
                   second: bool = False) -> dict:
    """The requests of every item with a sheet (``measure.json`` ``sheets``); ``only`` limits them to some ids."""
    sheets = measure_doc.get("sheets") or {}
    measures = measure_doc.get("measures") or {}
    reqs = []
    for it in items:
        rel = sheets.get(it["id"])
        m = measures.get(it["id"]) or {}
        if not rel or (only is not None and it["id"] not in only) or not m.get("sheet_sha256"):
            continue
        box = m.get("size") or it.get("bbox_m")
        reqs.append(request_item(it, f"../{rel}", m["sheet_sha256"], box, version, second))
    doc = {"kind": "library_audit_requests", "task": TASK2 if second else TASK, "version": version,
           "system_prompt": SYSTEM, "items": reqs}
    name = "requests2.json" if second else "requests.json"
    (Path(audit) / ASK_DIR).mkdir(parents=True, exist_ok=True)
    (Path(audit) / ASK_DIR / name).write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    return doc


def valid(data, kind: str, second: bool = False) -> bool:
    import jsonschema
    if data is None:
        return False
    v = jsonschema.Draft202012Validator(schema2(kind) if second else schema(kind))
    return not any(True for _ in v.iter_errors(data))


@dataclass(frozen=True)
class Model:
    key: str
    id: str
    slug: str


def model_of(key: str, model_id: Optional[str] = None, slug: Optional[str] = None,
             check_yaml: Optional[Path] = None) -> Model:
    """A check.yaml model key (any key: the agent model, a bake-off model) or an explicit id and slug."""
    if model_id:
        return Model(key or "custom", model_id, slug or model_id.split("/")[-1].lower())
    from wenart.recognition import answers as A
    models = A.load_models(check_yaml)
    if key not in models:
        raise KeyError(f"model key {key!r} is not in check.yaml models ({', '.join(models)})")
    m = models[key]
    return Model(key, str(m["id"]), str(m["slug"]))


def spec_for(second: bool):
    from wenart.assets import objaverse as OV
    return OV.JudgeSpec(dir_name=ASK_DIR, task=TASK2 if second else TASK, system=SYSTEM, label="library audit",
                        answers_kind="library_audit_answers", requests_kind="library_audit_requests",
                        schema_of=lambda item: schema2(item["context"]["kind"]) if second
                        else schema(item["context"]["kind"]),
                        valid_of=lambda item, data: valid(data, item["context"]["kind"], second))


def store_for(audit: Path, model: Model, second: bool = False):
    from wenart.assets import objaverse as OV
    name = f"answers2_{model.slug}.json" if second else f"answers_{model.slug}.json"
    store = OV._store_class()(Path(audit) / ASK_DIR / name, model.key, model.slug, model.id)
    store.spec = spec_for(second)
    store.data["kind"] = "library_audit_answers"
    return store


def load_answers(audit: Path, model: Model, second: bool = False) -> dict:
    """``{id: answer data}`` of the current, valid answers (stale or invalid ones are left out)."""
    name = "requests2.json" if second else "requests.json"
    p = Path(audit) / ASK_DIR / name
    if not p.is_file():
        return {}
    doc = json.loads(p.read_text(encoding="utf-8"))
    store = store_for(audit, model, second)
    out = {}
    for item in doc.get("items") or []:
        rec = store.valid(item)
        if rec is not None:
            out[item["context"]["id"]] = rec["data"]
    return out


def ask(audit: Path, model: Model, server: str, *, second: bool = False, workers: int = 4,
        deadline: Optional[float] = None, client_factory: Optional[Callable] = None, log: Callable = print) -> int:
    """Ask every request without a current answer (exit 0 all answered, 3 deadline, 2 server or answer failures)."""
    from wenart.assets import objaverse as OV
    name = "requests2.json" if second else "requests.json"
    p = Path(audit) / ASK_DIR / name
    if not p.is_file():
        log(f"audit ask: {p} not found: run the requests first")
        return EXIT_NOTHING
    items = json.loads(p.read_text(encoding="utf-8")).get("items") or []
    store = store_for(audit, model, second)
    pending = [i for i in items if store.valid(i) is None]
    if not pending:
        log(f"audit ask: all {len(items)} item(s) answered -> {store.path}")
        return EXIT_OK
    if client_factory is None:
        from wenart.recognition import vlm_client
        if not vlm_client.health(server):
            log(f"audit ask: no vLLM server answers at {server}")
            return EXIT_SERVER
        client = vlm_client.VLMClient(server, model=model.id, retries=3, timeout_s=600.0)
    else:
        client = client_factory(model, server)
    stats = OV.judge_ask(items, store, client, Path(audit), workers=workers, deadline=deadline, log=log,
                         spec=spec_for(second))
    log(f"audit ask{' pass 2' if second else ''}: {len(items)} item(s): {stats['asked']} asked "
        f"({stats['failed']} failed), {stats['reused']} reused, {stats['left']} left -> {store.path}")
    if stats["left"]:
        return EXIT_DEADLINE
    return EXIT_OK if all(store.valid(i) is not None for i in items) else EXIT_SERVER
