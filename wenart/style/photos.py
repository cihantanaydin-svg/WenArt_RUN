"""Style reference photos (docs/milestone5.md §6): floor, walls, light mood and style family from room photos.

What: a photo of a real room (``projects/<p>/style_photos/``) is used only
as a style reference for the slots the brief leaves open. Two vision models
read it independently (temperature 0, strict JSON schema); a value becomes a
term only when both models give it and it is not ``unclear``. No geometry,
furniture or layout is ever taken from a photo.

- ``photo_schema()``: the strict answer schema: ``floor`` (8 floor slugs),
  ``walls`` (5 wall slugs), ``light`` (5 light moods), ``family`` (9 style
  families), each an enum of the vocabulary plus ``unclear``; all four keys
  required, nothing else allowed. ``photo_prompt()`` lists the same options
  with the brief words of ``vocabulary.py`` (one source, cannot drift). Milestone 10 keeps these option lists
  (``PHOTO_FLOORS``, ``PHOTO_WALLS``, ``PHOTO_LIGHTS``) although the vocabulary grew: the new finishes and moods come
  from brief words only.
- ``read_pass(path, client, model_key)``: one call through
  ``client.run_schema`` (``wenart.recognition.vlm_client``, §1.5) -> a pass
  record ``{model_key, model, pass, data, error, raw_text, latency_s}``. A
  failed call keeps ``data: null`` and its error (never read as ``unclear``).
- ``read_style_photo(path, clients)``: one independent pass per client
  (``{"qwen": c1, "glm": c2}``) plus their agreement. ``python -m
  wenart.vision_check style-photo`` calls it with the one model its server
  holds and appends the result to a JSON file; ``combine`` agrees the passes.
- ``combine(records)``: the passes of every photo (several files, either
  model order) -> ``{"photos", "terms", "conflicts", "warnings"}``. Per photo
  the latest pass of each model counts; a slot of a photo is agreed when at
  least two models answered and all gave the same value (not ``unclear``).
  Photos that agree on different values for a slot are a ``conflict``: that
  slot gets no term. Every term carries its evidence ``{method: ai, model,
  pass, file}`` per model.
- ``wenart.style.profile.profile_from_brief(brief, photo_terms=terms)`` fills
  only slots the brief text does not name (§6).

Pass numbers follow ``wenart/vision_check/check.yaml`` (qwen pass 1, glm
pass 2).

CLI:
- ``python -m wenart.style.photos combine <passes.json> [...] --out <terms.json>``
- ``python -m wenart.style.photos read <photo> [...] --model-key qwen --server URL --out <passes.json>``
  (one pass per photo with the current server, appended; the same file
  layout as ``vision_check style-photo``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Optional

from wenart.style import vocabulary as V

SLOTS = ("floor", "walls", "light", "family")
UNCLEAR = "unclear"
IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")
PHOTO_DIR = "style_photos"


def _unique(values) -> list[str]:
    out: list[str] = []
    for v in values:
        if v not in out:
            out.append(v)
    return out


# Milestone 10 added many floors, wall finishes and light moods to the vocabulary. The photo question keeps the
# Milestone 5 options on purpose: two vision models must still agree on a short list, and the stored photo answers stay
# valid. The new finishes and moods come from brief words (wenart/style/profile.py), never from a photo.
PHOTO_FLOORS = ("wood_oak_light", "wood_walnut", "wood_parquet", "concrete_polished", "terracotta", "marble",
                "tiles_light", "carpet")
PHOTO_WALLS = ("plaster_white", "plaster_cream", "plaster_charcoal", "wood_panel", "brick")
PHOTO_LIGHTS = ("warm daylight", "cool daylight", "golden evening", "overcast", "night")

# Options per slot: the options above that the vocabulary still knows, in the order above (the order of the Milestone 5 prompt).
SLOT_VALUES: dict[str, list[str]] = {
    "floor": [s for s in PHOTO_FLOORS if s in {slug for _, slug in V.FLOOR_WORDS}],
    "walls": [s for s in PHOTO_WALLS if s in {slug for _, slug in V.WALL_WORDS}],
    "light": [m for m in PHOTO_LIGHTS if m in V.LIGHTING],
    "family": [name for name, _ in V.STYLE_FAMILIES],
}

SLOT_QUESTIONS = {
    "floor": "the floor surface",
    "walls": "the main wall finish",
    "light": "the light mood of the photo",
    "family": "the interior style family",
}


def _words(slot: str, value: str) -> list[str]:
    """The brief words of the vocabulary that give ``value`` (shown to the model as a hint)."""
    table = {"floor": V.FLOOR_WORDS, "walls": V.WALL_WORDS, "light": V.LIGHT_WORDS}.get(slot, [])
    return [kw for kw, v in table if v == value and kw != value]


# --------------------------------------------------------------------------
# Schema and prompt
# --------------------------------------------------------------------------

def photo_schema() -> dict:
    """Strict answer schema: four required slots, each the vocabulary enum plus ``unclear``."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "StylePhoto",
        "type": "object",
        "additionalProperties": False,
        "required": list(SLOTS),
        "properties": {slot: {"type": "string", "enum": SLOT_VALUES[slot] + [UNCLEAR]} for slot in SLOTS},
    }


def photo_prompt() -> str:
    """The prompt: what the photo is for, the options of every slot (with their brief words), when to say unclear."""
    lines = [
        "This photo shows a room. It is only a style reference: name the materials, the light and the style "
        "it shows. Nothing about the layout or the furniture is asked.",
        "For each field pick exactly one option from its list. Answer \"unclear\" when the photo does not show "
        "that part clearly, when two options fit about equally, or when no option fits. Do not guess.",
        "",
    ]
    for slot in SLOTS:
        options = []
        for value in SLOT_VALUES[slot]:
            words = _words(slot, value)
            options.append(f"{value} ({', '.join(words)})" if words else value)
        lines.append(f"{slot} ({SLOT_QUESTIONS[slot]}): " + "; ".join(options + [UNCLEAR]))
    lines += ["", "Answer with one JSON object with the keys " + ", ".join(SLOTS) + "."]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Calls
# --------------------------------------------------------------------------

def pass_numbers(keys) -> dict[str, int]:
    """``{model_key: pass number}``: the order of ``check.yaml`` models (qwen 1, glm 2), unknown keys after."""
    order: list[str] = []
    try:
        from wenart.vision_check.config import load_config
        order = list((load_config().get("models") or {}).keys())
    except Exception:  # noqa: BLE001 - the numbering then follows the given order
        order = []
    numbers = {k: i + 1 for i, k in enumerate(order)}
    nxt = len(order) + 1
    for k in keys:
        if k not in numbers:
            numbers[k] = nxt
            nxt += 1
    return {k: numbers[k] for k in keys}


def file_sha256(path) -> Optional[str]:
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except (OSError, TypeError):
        return None


def _photo_name(path) -> str:
    return Path(path).name if isinstance(path, (str, Path)) else "image"


def read_pass(path, client, model_key: str, pass_no: Optional[int] = None, *, seed: int = 0) -> dict:
    """One model's answer for one photo: ``{model_key, model, pass, data, error, raw_text, latency_s}``.

    ``client`` has ``.run_schema(images, prompt, schema, *, seed, task)``
    (``VLMClient`` or a fake). Any failure leaves ``data: null`` with the
    error; nothing raises for a bad answer or a transport problem.
    """
    if pass_no is None:
        pass_no = pass_numbers([model_key])[model_key]
    rec = {"model_key": model_key, "model": None, "pass": int(pass_no), "data": None, "error": None,
           "raw_text": "", "latency_s": None}
    try:
        result = client.run_schema([path], photo_prompt(), photo_schema(), seed=seed, task="style_photo")
    except Exception as exc:  # noqa: BLE001 - recorded, never silently dropped
        rec["error"] = f"{type(exc).__name__}: {exc}"
        rec["model"] = str(getattr(client, "model", None) or "?")
        return rec
    rec["model"] = str(getattr(result, "model", None) or getattr(client, "model", None) or "?")
    rec["raw_text"] = getattr(result, "raw_text", "") or ""
    latency = getattr(result, "latency_s", None)
    rec["latency_s"] = None if latency is None else round(float(latency), 3)
    error = getattr(result, "error", None)
    data = getattr(result, "data", None)
    if error is None and data is not None:
        from wenart.recognition.vlm_client import schema_errors
        problems = schema_errors(photo_schema(), data)
        if problems:
            error = "schema: " + "; ".join(problems[:5])
            data = None
    elif error is None:
        error = "no answer"
    rec["data"] = data if error is None else None
    rec["error"] = error
    return rec


def read_style_photo(path, clients: dict, *, seed: int = 0) -> dict:
    """One independent pass per client on one photo, plus their agreement (see ``agree``).

    ``clients``: ``{model_key: client}``; with a single client the result
    is a single pass (``single_pass: true``, no terms). Returns
    ``{"schema_version", "kind": "style_photo", "file", "sha256", "passes",
    "agreed", "terms", "unclear", "disagreements", "not_computed", "single_pass"}``.
    """
    numbers = pass_numbers(list(clients))
    passes = [read_pass(path, client, key, numbers[key], seed=seed) for key, client in clients.items()]
    name = _photo_name(path)
    out = {"schema_version": "0.1", "kind": "style_photo", "file": name,
           "sha256": file_sha256(path) if isinstance(path, (str, Path)) else None, "passes": passes}
    out.update(agree(passes, name))
    return out


# --------------------------------------------------------------------------
# Agreement
# --------------------------------------------------------------------------

def _evidence(p: dict, file: str) -> dict:
    return {"method": "ai", "model": p.get("model"), "pass": p.get("pass"), "file": file}


def agree(passes: list[dict], file: str) -> dict:
    """Agreement of the passes on one photo (the latest pass per model counts).

    Returns ``{"agreed": {slot: value}, "terms": [{slot, value, file,
    files, evidence}], "unclear": {slot: {key: value}}, "disagreements":
    {slot: {key: value}}, "single": {slot: {key: value}} (one valid pass
    only), "not_computed": [keys], "single_pass": bool}``.
    """
    latest: dict[str, dict] = {}
    for p in passes:
        latest[str(p.get("model_key"))] = p           # later passes of a model replace earlier ones
    valid = {k: p for k, p in latest.items() if isinstance(p.get("data"), dict) and not p.get("error")}
    not_computed = [k for k in latest if k not in valid]
    out = {"agreed": {}, "terms": [], "unclear": {}, "disagreements": {}, "single": {},
           "not_computed": not_computed, "single_pass": len(valid) < 2}
    for slot in SLOTS:
        answers = {k: p["data"].get(slot) for k, p in valid.items()}
        if not answers:
            continue
        if len(valid) < 2:
            out["single"][slot] = answers
            continue
        values = set(answers.values())
        if UNCLEAR in values:
            out["unclear"][slot] = answers
        elif len(values) == 1:
            value = next(iter(values))
            out["agreed"][slot] = value
            out["terms"].append({"slot": slot, "value": value, "file": file, "files": [file],
                                 "evidence": [_evidence(valid[k], file) for k in valid]})
        else:
            out["disagreements"][slot] = answers
    return out


def _passes_of(record: Any) -> list[tuple[str, Optional[str], dict]]:
    """``[(file, sha256, pass record)]`` of one stored record (see ``combine``)."""
    found: list[tuple[str, Optional[str], dict]] = []
    if not isinstance(record, dict):
        return found
    if isinstance(record.get("calls"), list):                      # a passes file
        for call in record["calls"]:
            found += _passes_of(call)
        return found
    if isinstance(record.get("passes"), list):                     # a read_style_photo result
        name = str(record.get("file") or "?")
        for p in record["passes"]:
            if isinstance(p, dict):
                found.append((Path(name).name, record.get("sha256"), p))
        return found
    if "result" in record or "model_key" in record:                # one call of vision_check style-photo
        name = Path(str(record.get("file") or "?")).name
        result = record.get("result")
        if isinstance(result, dict) and isinstance(result.get("passes"), list):
            for p in result["passes"]:
                if isinstance(p, dict):
                    found.append((Path(str(result.get("file") or name)).name, result.get("sha256")
                                  or record.get("sha256"), p))
        else:
            key = str(record.get("model_key") or "?")
            found.append((name, record.get("sha256"),
                          {"model_key": key, "model": record.get("model"), "pass": pass_numbers([key])[key],
                           "data": None, "error": record.get("error") or "no result"}))
    return found


def combine(records: list, sources: Optional[list[str]] = None) -> dict:
    """Terms of every photo from stored passes (see module docstring); pure.

    ``records``: passes files (``{"calls": [...]}``), ``read_style_photo``
    results, or single calls, in the order they were made.
    """
    by_file: dict[str, dict] = {}
    for record in records:
        for name, sha, p in _passes_of(record):
            entry = by_file.setdefault(name, {"sha256": sha, "passes": []})
            if sha and entry["sha256"] and sha != entry["sha256"]:
                # A changed photo: only its newest passes count.
                entry["passes"] = []
                entry.setdefault("notes", []).append("photo changed between passes; older passes dropped")
            if sha:
                entry["sha256"] = sha
            entry["passes"].append(p)
    photos: dict[str, dict] = {}
    warnings: list[str] = []
    for name in sorted(by_file):
        entry = by_file[name]
        res = agree(entry["passes"], name)
        photos[name] = {"sha256": entry["sha256"],
                        "passes": [{"model_key": p.get("model_key"), "model": p.get("model"), "pass": p.get("pass"),
                                    "ok": isinstance(p.get("data"), dict) and not p.get("error"),
                                    "error": p.get("error")} for p in entry["passes"]],
                        **{k: res[k] for k in ("agreed", "unclear", "disagreements", "single", "not_computed",
                                               "single_pass")}}
        if entry.get("notes"):
            photos[name]["notes"] = entry["notes"]
        if res["not_computed"]:
            warnings.append(f"{name}: no answer from {', '.join(res['not_computed'])} (not computed, not 'unclear')")
        if res["single_pass"]:
            warnings.append(f"{name}: fewer than two models answered: no term from this photo")
    terms, conflicts = [], []
    for slot in SLOTS:
        values: dict[str, str] = {name: p["agreed"][slot] for name, p in photos.items() if slot in p["agreed"]}
        if not values:
            continue
        if len(set(values.values())) > 1:
            conflicts.append({"slot": slot, "values": values})
            warnings.append(f"photos disagree on {slot}: " + ", ".join(f"{n} {v}" for n, v in values.items())
                            + "; no term for this slot")
            continue
        value = next(iter(values.values()))
        files = list(values)
        evidence = []
        for name in files:
            latest: dict[str, dict] = {}
            for p in by_file[name]["passes"]:
                latest[str(p.get("model_key"))] = p
            evidence += [_evidence(p, name) for p in latest.values()
                         if isinstance(p.get("data"), dict) and not p.get("error")]
        terms.append({"slot": slot, "value": value, "file": files[0], "files": files, "evidence": evidence})
    return {"schema_version": "0.1", "kind": "style_photo_terms", "sources": list(sources or []),
            "photos": photos, "terms": terms, "conflicts": conflicts, "warnings": warnings}


# --------------------------------------------------------------------------
# Files
# --------------------------------------------------------------------------

def style_photo_paths(project_dir, brief: Optional[dict] = None) -> tuple[list[Path], list[str]]:
    """``(photos, warnings)``: the brief's ``style_photos`` (file names in ``<project_dir>/style_photos/``),
    or every image there when the list is empty (``brief`` is a ``wenart.brief.load_brief`` result)."""
    folder = Path(project_dir) / PHOTO_DIR
    names = list(((brief or {}).get("values") or {}).get("style_photos") or [])
    warnings: list[str] = []
    if names:
        paths = []
        for n in names:
            p = folder / str(n)
            if p.is_file():
                paths.append(p)
            else:
                warnings.append(f"brief style_photos: {p} not found")
        return paths, warnings
    if not folder.is_dir():
        return [], warnings
    return sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES), warnings


def _read_json(path: Path) -> Optional[dict]:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def append_call(out: Path, photo: Path, model_key: str, result: Optional[dict], error: Optional[str] = None,
                seconds: Optional[float] = None) -> dict:
    """Append one photo's pass to a passes file (``{"calls": [...]}``, the ``vision_check style-photo`` layout);
    an older call of the same photo and model is replaced."""
    data = _read_json(out) or {"schema_version": "0.1", "kind": "style_photo_passes", "calls": []}
    model = None
    if result:
        model = next((p.get("model") for p in result.get("passes") or []), None)
    rec = {"file": str(photo), "sha256": file_sha256(photo), "model_key": model_key, "model": model,
           "result": result, "error": error, "seconds": seconds}
    data["calls"] = [c for c in data.get("calls") or []
                     if not (c.get("file") == str(photo) and c.get("model_key") == model_key)]
    data["calls"].append(rec)
    _write_json(out, data)
    return data


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _default_factory(model_key: str, base_url: str):
    from wenart.vision_check.config import client_factory
    return client_factory(model_key, base_url)


def main(argv=None, client_factory=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.style.photos",
                                     description="style reference photos: read one pass, or combine the passes")
    sub = parser.add_subparsers(dest="command", required=True)
    p_comb = sub.add_parser("combine", help="agree the stored passes -> terms JSON")
    p_comb.add_argument("passes", nargs="+", help="passes JSON file(s) (vision_check style-photo or 'read' output)")
    p_comb.add_argument("--out", required=True, help="terms JSON (input of wenart.style --photo-terms)")
    p_read = sub.add_parser("read", help="one pass per photo with the current server, appended to --out")
    p_read.add_argument("photos", nargs="+", help="photo files")
    p_read.add_argument("--model-key", required=True, help="check.yaml model key (qwen or glm)")
    p_read.add_argument("--server", default="http://127.0.0.1:8001/v1", help="vLLM base URL")
    p_read.add_argument("--out", required=True, help="passes JSON (appended)")
    args = parser.parse_args(argv)

    if args.command == "combine":
        records, sources = [], []
        for name in args.passes:
            path = Path(name)
            data = _read_json(path)
            if data is None:
                print(f"style photos: {path} not found", file=sys.stderr)
                return 2
            records.append(data)
            sources.append(path.as_posix())
        terms = combine(records, sources)
        _write_json(Path(args.out), terms)
        for t in terms["terms"]:
            print(f"term {t['slot']} = {t['value']} ({', '.join(t['files'])})")
        for w in terms["warnings"]:
            print(f"note: {w}")
        print(f"{len(terms['terms'])} term(s) from {len(terms['photos'])} photo(s) -> {args.out}")
        return 0

    factory = client_factory or _default_factory
    client = factory(args.model_key, args.server)
    out = Path(args.out)
    for name in args.photos:
        photo = Path(name)
        if not photo.is_file():
            append_call(out, photo, args.model_key, None, error="photo not found")
            print(f"style photos [{args.model_key}]: {photo}: not found")
            continue
        result = read_style_photo(photo, {args.model_key: client})
        err = next((p["error"] for p in result["passes"] if p.get("error")), None)
        append_call(out, photo, args.model_key, result, error=err,
                    seconds=sum(p.get("latency_s") or 0.0 for p in result["passes"]))
        print(f"style photos [{args.model_key}]: {photo.name}: {err or result['passes'][0]['data']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
