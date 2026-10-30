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

3D Warehouse layer (23 Oct 2026, the user's request: "runs the existing audit (render, vision quality, logo check)"):

- What: the question version ``ask.version_logo`` (m13.2) for the models of ``LOGO_SOURCES`` (``3dwh``) adds
  ``brand_logo`` (a maker's logo or brand name readable on the model) and ``text_print`` (decorative lettering);
  ``decide.py`` removes a model with either (the reasons of ``checks.RENDER_FINDINGS``). The server's guided schema of
  an m13.2 request is the m13.2 schema (``server_schema``: ``context.version``).
- Why: the existing logo check reads titles (``branded``) and the logos a run's render showed (``render_findings``);
  a 3D Warehouse upload of a branded product shows its logo before any run.
- How: ``context.version`` is no part of a request's ``input_sha256``: every stored answer stays valid and is reused;
  ``valid`` reads the version from the answer's fields (``answer_version``). Found on the way (not changed): the
  m12.1 and m13.1 requests keep the m12.1 guided schema, so the m13.1 ``materials`` never come back (no stored answer
  of pods P2-P2c carries them). Giving them their own schema is not enough: the write step would then store the
  tags, ``version_for`` would switch those models to the m12.1 question and the next run would ask them again. An
  m13.2 model keeps its version whatever its tags (``LOGO_SOURCES`` first).

Doors and windows (28 Oct 2026, the user: "I want better doors inside the house and the outside ... find the best
models"): the question version ``ask.version_openings`` (m13.3 = m13.2 plus ``OPENING_FIELDS``: role, operation,
leaves, glazing, leaf, handle side) for the doors and windows of ``OPENING_SOURCES`` (the HSSD ones); its guided schema
is its own (``server_schema``), ``answer_version`` reads it from the fields; the 3D Warehouse doors keep m13.2.
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
    from wenart.assets import warehouse as WH
    from wenart.furniture import catalog as C
    if kind in WH.EXTRA_KINDS:                        # 23 Oct 2026: trees, doors, windows, objects
        return list(WH.EXTRA_KINDS[kind])
    if kind == "decor":
        return list(C.DECOR_TYPES)
    return [t for t in C.FURNITURE_TYPES if t not in ("unknown", "stair", "kitchen_counter", "kitchen_island",
                                                      "wall_cabinet")]


def type_words(ftype: str, kind: str) -> tuple[str, str]:
    from wenart.assets import objaverse as OV
    from wenart.assets import warehouse as WH
    if kind in WH.EXTRA_KINDS:
        if ftype == WH.UNTYPED_OBJECT:
            return "object", "an object of no known type"
        name = ftype.replace("_model", "").replace("_", " ")
        return name, f"{name} ({kind})"
    if kind == "decor":
        name, what, _ = OV.DECOR_WORDS.get(ftype, (ftype.replace("_", " "), ftype.replace("_", " "), ""))
        return name, what
    return OV.TYPE_WORDS.get(ftype, (ftype.replace("_", " "), ftype.replace("_", " ")))


# Milestone 13 (audit gate "material tags judged for every entry"): the materials a model shows, asked with the
# question version ``ask.version_materials`` (m13.1) of models without ``material_tags``; models that carry tags keep
# the m12.1 question so their stored answers stay valid. The words are the design enum of recolour.TAG_ORDER + other.
MATERIAL_WORDS: tuple[str, ...] = ("glass", "wood", "metal", "fabric", "rattan", "marble", "leather", "stone",
                                   "ceramic", "plastic", "other")


def materials_version(cfg_ask: dict) -> str:
    return str(cfg_ask.get("version_materials") or "m13.1")


# 23 Oct 2026 (the 3D Warehouse layer, the user's request "runs the existing audit (render, vision quality, logo
# check)"): the question version ``ask.version_logo`` (m13.2) adds the logo and print fields (``LOGO_FIELDS``) for the
# models of these sources; every other model keeps its question, so its stored answer stays valid.
LOGO_SOURCES: tuple[str, ...] = ("3dwh",)
LOGO_FIELDS: tuple[str, ...] = ("brand_logo", "text_print")


def logo_version(cfg_ask: dict) -> str:
    return str(cfg_ask.get("version_logo") or "m13.2")


# 28 Oct 2026 (user: "I want better doors inside the house and the outside ... find the best models"): the question
# version ``ask.version_openings`` (m13.3: the m13.2 question plus these fields) for the doors and windows of
# ``OPENING_SOURCES``: where the model belongs, how it opens, its leaves, its glass, its leaf and its handle side
# (``opening_models`` reads them: an inside door never goes on the facade, a terrace door is glazed, a sliding door
# opens as drawn, a door is mirrored to its drawn hinge). The 3D Warehouse doors keep their m13.2 answers.
OPENING_SOURCES: tuple[str, ...] = ("hssd",)
OPENING_ROLES: tuple[str, ...] = ("entrance", "outside", "inside", "garage", "window", "unclear")
OPENING_OPERATIONS: tuple[str, ...] = ("hinged", "sliding", "folding", "pivot", "casement", "tilt_turn", "awning",
                                       "hung", "fixed", "unclear")
GLAZINGS: tuple[str, ...] = ("none", "clear", "bars", "patterned", "unclear")
LEAF_LOOKS: tuple[str, ...] = ("flush", "panelled", "glazed", "louvred", "plank", "frame_only", "unclear")
HANDLE_SIDES: tuple[str, ...] = ("left", "right", "both", "none", "unclear")
OPENING_FIELDS: tuple[str, ...] = ("role", "operation", "leaves", "glazing", "leaf", "handle_side")


def opening_version(cfg_ask: dict) -> str:
    return str(cfg_ask.get("version_openings") or "m13.3")


def with_openings(version: Optional[str]) -> bool:
    """True when a question version asks for the opening fields (m13.3 and later; for kind ``opening`` only)."""
    return _version_number(version) >= (13, 3)


def opening_props() -> dict:
    return {"role": {"enum": list(OPENING_ROLES)}, "operation": {"enum": list(OPENING_OPERATIONS)},
            "leaves": {"type": "integer", "minimum": 0, "maximum": 8}, "glazing": {"enum": list(GLAZINGS)},
            "leaf": {"enum": list(LEAF_LOOKS)}, "handle_side": {"enum": list(HANDLE_SIDES)}}


# 30 Oct 2026 (lesson UL180; user: "put some pillows and sheet on to the white sofa"): up to m13.3 ``has_cushions`` asked
# for "loose or scatter cushions", so a sofa with loose seat and back cushions and no pillow on it was flagged and the
# decor left it bare. From m13.4 the question splits them: ``has_cushions`` the loose seat or back cushions,
# ``has_scatter_cushions`` the pillows lying on it (``catalog.has_scatter_cushions`` reads it; until a model is asked
# again its title decides). ``ask.version_seats`` in audit.yaml (opt-in: it re-asks every seat and bed model) gives the
# seats and beds that question.
SCATTER_VERSION: tuple[int, int] = (13, 4)
BED_QUESTION_TYPES: tuple[str, ...] = ("bed_single", "bed_double", "bunk_bed", "crib")
SEAT_QUESTION_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "chair", "bench", "ottoman",
                                        "office_chair", "bar_stool")


def with_scatter(version: Optional[str]) -> bool:
    """True when a question version splits loose seat cushions from scatter cushions (m13.4 and later)."""
    return _version_number(version) >= SCATTER_VERSION


def version_for(item: dict, cfg_ask: dict) -> str:
    """The question version of one model: ``version_openings`` for a door or window of ``OPENING_SOURCES`` (28 Oct
    2026), ``version_seats`` for a seat or bed when set (30 Oct 2026, UL180), ``version_logo`` for a model of
    ``LOGO_SOURCES``, ``version_materials`` for a model without material tags (the question asks for them), else
    ``version``."""
    if item.get("kind") == "opening" and item.get("source") in OPENING_SOURCES:
        return opening_version(cfg_ask)
    if cfg_ask.get("version_seats") and item.get("type") in SEAT_QUESTION_TYPES + BED_QUESTION_TYPES:
        return str(cfg_ask["version_seats"])
    if item.get("source") in LOGO_SOURCES:
        return logo_version(cfg_ask)
    tags = item.get("material_tags")
    if isinstance(tags, list) and tags:
        return str(cfg_ask.get("version", "m12.1"))
    return materials_version(cfg_ask)


def _version_number(version: Optional[str]) -> tuple[int, int]:
    """``m13.2`` -> ``(13, 2)``; ``(0, 0)`` for a word that is no question version."""
    word = str(version or "").strip().lower()
    if not word.startswith("m"):
        return (0, 0)
    major, _, minor = word[1:].partition(".")
    return (int(major) if major.isdigit() else 0, int(minor) if minor.isdigit() else 0)


def with_materials(version: Optional[str]) -> bool:
    """True when a question version asks for the materials (m13 and later: the milestone number after the ``m``)."""
    # by number, not by string order ("m2" > "m13" as text; review fix of 15 Oct 2026)
    return _version_number(version)[0] >= 13


def with_logo(version: Optional[str]) -> bool:
    """True when a question version asks for the logo and print fields (m13.2 and later)."""
    return _version_number(version) >= (13, 2)


def schema(kind: str, version: Optional[str] = None) -> dict:
    """Pass 1 schema (strict; nullable fields answer null where they do not apply). With a Milestone 13 ``version``
    the answer also names the ``materials`` (``MATERIAL_WORDS``)."""
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
    if with_scatter(version):
        props["has_scatter_cushions"] = {"type": ["boolean", "null"]}
    if with_materials(version):
        props["materials"] = {"type": "array", "items": {"enum": list(MATERIAL_WORDS)}, "maxItems": 4}
    if with_logo(version):
        props.update({f: {"type": "boolean"} for f in LOGO_FIELDS})
    if with_openings(version) and kind == "opening":
        props.update(opening_props())
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "LibraryAudit", "type": "object",
            "additionalProperties": False, "required": list(props), "properties": props}


def schema2(kind: str) -> dict:
    """Pass 2 schema: the type only."""
    return {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "LibraryAuditType", "type": "object",
            "additionalProperties": False, "required": ["type_guess"],
            "properties": {"type_guess": {"enum": kind_types(kind) + ["other"]}}}


def _fmt(box) -> str:
    return " x ".join(f"{float(v):.2f}" for v in box)


def prompt(item: dict, box, version: Optional[str] = None) -> str:
    """The pass 1 question of one model (the same text for every model of a type but the facts); a Milestone 13
    ``version`` adds the materials field."""
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
        (("- has_cushions: true when it has loose seat or back cushions; has_scatter_cushions: true when decorative "
          "scatter or throw pillows lie on it (on the seat, against the back or the headboard)" if (bed or seat)
          else "- has_cushions: null; has_scatter_cushions: null.") if with_scatter(version) else
         "- has_cushions: true when it has loose or scatter cushions" if (bed or seat)
         else "- has_cushions: null."),
        ("- contact: how it rests: flat_bottom (stands on a surface), hangs (on a wall or from a ceiling), leans "
         "(against a back or a wall), drapes (lies over a host like a throw)" if item["kind"] == "decor"
         else "- contact: null."),
    ]
    if with_materials(version):
        fields.append("- materials: the visible materials of the model, up to four, from: " + ", ".join(MATERIAL_WORDS)
                      + " (the main one first; 'other' when none of the words fits).")
    if with_logo(version):
        fields += ["- brand_logo: true when a maker's logo or brand name can be read on the model (in its shape or "
                   "its texture); the header text above the renders does not count.",
                   "- text_print: true when decorative lettering or text is printed on its visible surface (the "
                   "functional labels of an appliance's control panel do not count)."]
    if with_openings(version) and item["kind"] == "opening":
        fields += [
            "- role: where a designer would put it: 'entrance' (the front door of a house: a solid or statement "
            "leaf, often wider or with side lights), 'outside' (a back, service, terrace or balcony door), 'inside' (a "
            "door between rooms: a light interior leaf), 'garage', 'window', 'unclear'.",
            "- operation: how it opens: hinged, sliding, folding, pivot (doors); casement, tilt_turn, awning, hung, "
            "sliding, fixed (windows); 'unclear' when you cannot tell.",
            "- leaves: how many door leaves or window sashes it has side by side (0 when you cannot tell).",
            "- glazing: 'none' (no glass), 'clear' (clear glass without bars), 'bars' (clear glass divided by "
            "glazing bars or muntins into small panes), 'patterned' (frosted, textured, stained or decorated glass), "
            "'unclear'.",
            "- leaf: the look of the door leaf or the window sash: flush (a plain flat leaf), panelled (raised or "
            "sunk panels), glazed (mostly glass in a frame), louvred, plank (boards or a barn door), frame_only (a "
            "window: a frame round the glass), 'unclear'.",
            "- handle_side: on which side of the leaf the handle is in tile 0: 'left' or 'right' of the image, "
            "'both' (a pair), 'none' (no handle can be seen), 'unclear'."]
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
    p = prompt2(item) if second else prompt(item, box, version)
    sch = schema2(item["kind"]) if second else schema(item["kind"], version)
    task = TASK2 if second else TASK
    desc = {"version": version, "task": task, "system": SYSTEM, "prompt": p, "schema": sch, "sheet": sheet_px}
    return {"key": f"audit_{item['id']}", "task": task, "images": [sheet_rel], "prompt": p,
            "context": {"id": item["id"], "type": item["type"], "kind": item["kind"], "pass": 2 if second else 1,
                        "version": version},
            "input_sha256": _sha(desc)}


def build_requests(items: list[dict], measure_doc: dict, audit: Path, version: str, only: Optional[set] = None,
                   second: bool = False, cfg_ask: Optional[dict] = None) -> dict:
    """The requests of every item with a sheet (``measure.json`` ``sheets``); ``only`` limits them to some ids.
    Milestone 13: with ``cfg_ask`` (the ``ask`` block of audit.yaml) a pass 1 request takes ``version_for(item)``
    (the materials question for models without material tags), else ``version`` for every item."""
    sheets = measure_doc.get("sheets") or {}
    measures = measure_doc.get("measures") or {}
    reqs = []
    for it in items:
        rel = sheets.get(it["id"])
        m = measures.get(it["id"]) or {}
        if not rel or (only is not None and it["id"] not in only) or not m.get("sheet_sha256"):
            continue
        box = m.get("size") or it.get("bbox_m")
        v = version if (second or not cfg_ask) else version_for(it, cfg_ask)
        reqs.append(request_item(it, f"../{rel}", m["sheet_sha256"], box, v, second))
    doc = {"kind": "library_audit_requests", "task": TASK2 if second else TASK, "version": version,
           "system_prompt": SYSTEM, "items": reqs}
    name = "requests2.json" if second else "requests.json"
    (Path(audit) / ASK_DIR).mkdir(parents=True, exist_ok=True)
    (Path(audit) / ASK_DIR / name).write_text(json.dumps(doc, indent=1, ensure_ascii=False), encoding="utf-8")
    return doc


def answer_version(data) -> Optional[str]:
    """The question version an answer's fields show: m13.2 (the logo fields), m13.1 (the materials), else None
    (the m12.1 question)."""
    if not isinstance(data, dict):
        return None
    if any(f in data for f in OPENING_FIELDS):
        return opening_version({})
    if any(f in data for f in LOGO_FIELDS):
        return logo_version({})
    return materials_version({}) if "materials" in data else None


def valid(data, kind: str, second: bool = False) -> bool:
    """An answer of any question: the m12.1 one, the m13.1 one with its ``materials``, the m13.2 one with the logo
    fields too."""
    import jsonschema
    if data is None:
        return False
    sch = schema2(kind) if second else schema(kind, answer_version(data))
    v = jsonschema.Draft202012Validator(sch)
    return not any(True for _ in v.iter_errors(data))


@dataclass(frozen=True)
class Model:
    key: str
    id: str
    slug: str


def model_of(key: str, model_id: Optional[str] = None, slug: Optional[str] = None,
             check_yaml: Optional[Path] = None) -> Model:
    """A check.yaml model key (any key: the agent model; a dotted key names a nested entry, as the bake-off's
    ``bakeoff.fp8`` that ``wenart.run.servers`` serves) or an explicit id and slug."""
    if model_id:
        return Model(key or "custom", model_id, slug or model_id.split("/")[-1].lower())
    from wenart.recognition import answers as A
    node = A.load_models(check_yaml)
    for part in str(key).split("."):
        node = node.get(part) if isinstance(node, dict) else None
    if not isinstance(node, dict) or not node.get("id"):
        raise KeyError(f"model key {key!r} is not in check.yaml models")
    return Model(key, str(node["id"]), str(node.get("slug") or str(node["id"]).split("/")[-1].lower()))


def server_schema(item: dict) -> dict:
    """The guided-decoding schema of a pass 1 request: its own version's schema for an m13.2 request (the logo
    fields; module docstring) or a later one (m13.3: the opening fields of a door or window, 28 Oct 2026), else the
    m12.1 schema (unchanged: see the module docstring for the m13.1 gap)."""
    version = item["context"].get("version")
    return schema(item["context"]["kind"], version if with_logo(version) else None)


def spec_for(second: bool):
    from wenart.assets import objaverse as OV
    return OV.JudgeSpec(dir_name=ASK_DIR, task=TASK2 if second else TASK, system=SYSTEM, label="library audit",
                        answers_kind="library_audit_answers", requests_kind="library_audit_requests",
                        schema_of=lambda item: schema2(item["context"]["kind"]) if second else server_schema(item),
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
