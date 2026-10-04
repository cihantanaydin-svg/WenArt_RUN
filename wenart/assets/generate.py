"""Generated furniture models: Z-Image-Turbo text-to-image, then TRELLIS.2-4B image-to-3D (docs/milestone8.md §3).

What: for every (furniture type, style family) pair that has no accepted library model (ABO, Poly Haven,
Objaverse), a few textured GLBs are generated and handed to the library pipeline as survey candidates
(``survey_generated.json``, the record shape of ``survey.json`` plus the M8 fields). Thumbnails, judging and
acceptance then treat them like any other model; a generated model is used only when no real model fits.

1. ``plan`` (CPU): reads the accepted list(s) / catalogue(s) and lists the gaps -> ``<out>/generate/plan.json``.
   A model counts for a pair when it is accepted (accepted lists) or a non-parametric catalogue entry, is furniture
   (not decor), lists the family or ``neutral`` in ``styles`` and, for a bed, has a mattress or is a bed frame.
   Types: every ``wenart.furniture.catalog.FURNITURE_TYPES`` entry except the fixed equipment of ``generate.yaml``
   (``stair``, ``kitchen_counter``, ``kitchen_island``, ``unknown``). The Poly Haven ``catalog.json`` is always
   read too (``--no-polyhaven`` to leave it out).
2. ``run`` (venv-trellis, GPU): phase A renders every missing image with Z-Image-Turbo (prompt template of
   ``generate.yaml``, 1024 x 1024, 8 steps, guidance 0, CPU generator seeded per pair and image), then frees it;
   phase B loads TRELLIS.2 once and turns every image into a GLB (``Trellis2ImageTo3DPipeline.run`` at the
   pipeline's default resolution, ``o_voxel.postprocess.to_glb`` with about 200k faces and 2048 px textures).
   Images go first index by index (image 1 of every pair, then image 2), so a deadline cut leaves one model per pair
   before second ones. Every item is resumable: an image is done when its JSON holds the current key (prompt, seed,
   model revision, settings) and the PNG still has the recorded sha256; a model when its JSON holds the key (image
   sha256, seed, every model revision, the TRELLIS.2 commit, export settings) and the GLB its sha256. A failed
   model is not retried with the same key unless ``--retry-failed``. The deadline (``--deadline`` or
   ``WENART_DEADLINE``, epoch s) is checked before every load and item against the measured (or estimated) time:
   exit 3 when cut, after writing the survey of what is done.
3. ``survey`` (CPU, also the last step of ``run``): ``<out>/survey_generated.json``.

Compatibility shims (TRELLIS.2 @ the pinned commit with transformers 5.18.0, the version validated with
Z-Image-Turbo by the polish): transformers 5 moved the DINOv3 ViT blocks from ``model.layer`` to
``model.model.layer`` (the checkpoint keys are renamed on load), so ``DinoV3FeatureExtractor.extract_features`` is
replaced by the same computation that finds the blocks in either place; transformers 5 loads checkpoints in their
stored dtype (``dtype="auto"``), so the fp16 BiRefNet is cast to float32, the dtype TRELLIS.2 feeds it. The
background remover is the MIT BiRefNet instead of the gated, non-commercial RMBG-2.0 named in ``pipeline.json``
(``generate.yaml``); every model is read from its pinned local snapshot (no hub lookups).

The module imports only the standard library and stdlib-only wenart modules at the top: ``plan``, ``survey`` and the
record helpers run on the CPU (tests/test_generate.py); torch, diffusers and trellis2 are imported by the GPU
backends only.

CLI::

    python -m wenart.assets.generate plan --catalog FILE [--catalog FILE ...] --families F1,F2 --out DIR
        [--types T1,T2] [--images-per-pair N] [--no-polyhaven]
    python -m wenart.assets.generate run --out DIR --plan FILE [--images-per-pair N] [--deadline T] [--retry-failed]
    python -m wenart.assets.generate survey --out DIR --plan FILE [--images-per-pair N]

Exit codes: 0 done, 1 nothing usable (every model failed, a backend did not load), 2 usage error (unknown family
or type, unreadable catalogue or plan), 3 cut by the deadline.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.assets.objaverse import (canonical_sha256, deadline_of, glb_info, glb_json, now_utc, read_json,
                                     sha256_file, write_json)

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "generate.yaml"
POLYHAVEN_CATALOG = HERE.parent / "furniture" / "catalog.json"
SCHEMA_VERSION = "0.1"
SOURCE = "generated"
CODE_VERSION = "m8.1"                 # part of every item key: bump when the generation itself changes
GEN_DIR = "generate"
PLAN_NAME = "plan.json"
SURVEY_NAME = "survey_generated.json"
UID_PREFIX = "gen_"
EXIT_OK, EXIT_FAIL, EXIT_USAGE, EXIT_DEADLINE = 0, 1, 2, 3
# The candidate fields of survey.json (wenart.assets.objaverse.survey) and the fields milestone 8 adds.
SURVEY_FIELDS = ("uid", "group", "types", "categories", "title", "author", "source_url", "licence", "licence_raw",
                 "face_count", "glb_size_meta", "texture_count", "likes", "views", "prefer_hit", "object_path", "rank",
                 "glb", "glb_sha256", "glb_bytes", "glb_info")
NEW_FIELDS = ("source", "licence_flag", "units_known", "kind", "decor_type", "style_hint", "generated", "generation")
GENERATED_KEYS = ("prompt", "image_sha256", "model", "revision", "seed")
ALLOC_CONF = "expandable_segments:True"
TRELLIS_ENV_NAME = "trellis_env.json"  # written into venv-trellis by scripts/pod_setup_trellis.sh


class UsageError(ValueError):
    """A bad argument, family, type, catalogue or plan (exit 2)."""


def log_print(*args) -> None:
    print(*args, flush=True)


# --------------------------------------------------------------------------
# Configuration and naming
# --------------------------------------------------------------------------

def load_config(path: Optional[Path] = None) -> dict:
    import yaml
    return yaml.safe_load(Path(CONFIG_PATH if path is None else path).read_text(encoding="utf-8")) or {}


def known_families() -> list[str]:
    """The style families (``wenart.style.vocabulary.STYLE_FAMILIES``), without ``neutral``."""
    from wenart.furniture import catalog as C
    return [s for s in C.style_values() if s != C.NEUTRAL]


def plan_types(cfg: dict) -> list[str]:
    """Every furniture type except the fixed equipment of ``exclude_types``, in catalogue order."""
    from wenart.furniture import catalog as C
    excluded = set(cfg.get("exclude_types") or ())
    return [t for t in C.FURNITURE_TYPES if t not in excluded]


def decor_types(cfg: dict) -> list[str]:
    """The decor types the generator makes (Milestone 9, ``generate.yaml decor_types``: vase, bowl, plant_small)."""
    return [str(t) for t in (cfg.get("decor_types") or ())]


def target_types(cfg: dict) -> list[str]:
    """The types of a target plan (docs/milestone9.md §2.3): every generated furniture type, then the decor types."""
    return plan_types(cfg) + [t for t in decor_types(cfg) if t not in plan_types(cfg)]


def family_slug(family: str) -> str:
    return family.strip().replace(" ", "_")


def pair_id(ftype: str, family: str) -> str:
    return f"{ftype}__{family_slug(family)}"


def split_list(values) -> list[str]:
    """``["a,b", "c"]`` or ``"a, b"`` -> ``["a", "b", "c"]`` (order kept, duplicates and blanks dropped)."""
    if isinstance(values, str):
        values = [values]
    out: list[str] = []
    for value in values or ():
        for part in str(value).split(","):
            part = " ".join(part.split())
            if part and part not in out:
                out.append(part)
    return out


def parse_families(values) -> list[str]:
    known = known_families()
    fams = split_list(values)
    if fams == ["all"]:
        return known
    if not fams:
        raise UsageError("no style family given (--families F1,F2 or all)")
    unknown = [f for f in fams if f not in known]
    if unknown:
        raise UsageError(f"unknown style famil{'y' if len(unknown) == 1 else 'ies'} {unknown} "
                         f"(known: {', '.join(known)})")
    return fams


def parse_types(values, cfg: dict, target: bool = False) -> list[str]:
    allowed = target_types(cfg) if target else plan_types(cfg)
    types = split_list(values)
    if not types:
        return allowed
    bad = [t for t in types if t not in allowed]
    if bad:
        raise UsageError(f"type(s) {bad} cannot be generated (allowed: {', '.join(allowed)}; fixed equipment "
                         f"{', '.join(cfg.get('exclude_types') or [])} never is)")
    return [t for t in allowed if t in types]


def seed_for(ftype: str, family: str, index: int, base: int = 0) -> int:
    """Seed of image ``index`` (1-based) of a pair: stable, independent of the plan's order and size."""
    digest = hashlib.sha256(f"{ftype}|{family}|{int(index)}".encode("utf-8")).hexdigest()
    return (int(base) + int(digest[:8], 16)) % 2 ** 31


def prompt_for(ftype: str, family: str, cfg: dict) -> str:
    """The fixed prompt template filled with the type words and the family's hints (furniture or fixtures)."""
    words = cfg["type_words"][ftype]
    group = "fixtures" if ftype in (cfg.get("fixture_types") or ()) else "furniture"
    if ftype in decor_types(cfg):
        group = "decor"                                       # Milestone 9: the family's decor hints
    hints = cfg["family_hints"][family][group]
    text = cfg["prompt_template"].format(family=family, type_words=words, hints=hints)
    return " ".join(text.split())


def uid_for(ftype: str, family: str, index: int, glb_sha256: str) -> str:
    """``gen_<type>_<family>_<n>_<sha8>`` (family spaces -> underscores; sha8 of the GLB)."""
    return f"{UID_PREFIX}{ftype}_{family_slug(family)}_{int(index)}_{glb_sha256[:8]}"


def config_sha256(cfg: dict) -> str:
    return canonical_sha256(cfg)


# --------------------------------------------------------------------------
# Plan (CPU)
# --------------------------------------------------------------------------

def read_catalog(path: Path) -> tuple[str, list[dict]]:
    """``("accepted", records)`` for an accepted list (``wenart.assets.objaverse accept``), ``("catalog",
    entries)`` for a catalogue file with ``entries`` (Poly Haven ``catalog.json``, ``catalog_library.json``)."""
    path = Path(path)
    if not path.is_file():
        raise UsageError(f"catalogue {path} not found")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise UsageError(f"catalogue {path} is not readable JSON: {exc}") from exc
    if isinstance(data, dict) and isinstance(data.get("accepted"), list):
        return "accepted", [r for r in data["accepted"] if isinstance(r, dict)]
    if isinstance(data, dict) and isinstance(data.get("entries"), list):
        return "catalog", [r for r in data["entries"] if isinstance(r, dict)]
    raise UsageError(f"{path}: neither an accepted list ('accepted': [...]) nor a catalogue ('entries': [...])")


def usable(rec: dict, fmt: str) -> tuple[bool, str]:
    """Whether a record can fill a (type, family) pair, else the reason it cannot."""
    from wenart.furniture import catalog as C
    if fmt == "accepted" and rec.get("accepted") is not True:
        return False, "not accepted"
    if rec.get("parametric"):
        return False, "parametric entry"
    if (rec.get("kind") or "furniture") != "furniture":
        return False, "decor"
    styles = rec.get("styles")
    if not isinstance(styles, list) or not styles:
        return False, "no styles"
    if rec.get("type") in C.BED_TYPES and not (rec.get("has_mattress") is True or rec.get("bed_frame") is True):
        return False, "bed without a mattress and not a bed frame"
    return True, ""


def record_id(rec: dict) -> str:
    return str(rec.get("id") or rec.get("uid") or "?")


def make_plan(catalogs: list[Path], families: list[str], out: Path, cfg: Optional[dict] = None,
              types: Optional[list[str]] = None, images_per_pair: Optional[int] = None,
              log: Callable = log_print) -> dict:
    """The (type, family) pairs without a usable model -> ``<out>/generate/plan.json``."""
    from wenart.furniture import catalog as C
    cfg = cfg or load_config()
    out = Path(out)
    types = list(types) if types else plan_types(cfg)
    n_images = int(images_per_pair or cfg.get("images_per_pair") or 2)
    if n_images < 1:
        raise UsageError("--images-per-pair must be at least 1")
    sources = []
    by_type: dict[str, list[tuple[str, list[str]]]] = {}
    skipped_by_type: dict[str, dict[str, int]] = {}
    for path in catalogs:
        fmt, records = read_catalog(path)
        info = {"path": str(path), "format": fmt, "sha256": sha256_file(path), "records": len(records), "usable": 0,
                "skipped": {}}
        for rec in records:
            ftype = rec.get("type")
            if ftype not in C.FURNITURE_TYPES:
                continue
            ok, reason = usable(rec, fmt)
            if not ok:
                info["skipped"][reason] = info["skipped"].get(reason, 0) + 1
                per = skipped_by_type.setdefault(ftype, {})
                per[reason] = per.get(reason, 0) + 1
                continue
            info["usable"] += 1
            by_type.setdefault(ftype, []).append((record_id(rec), [str(s) for s in rec["styles"]]))
        sources.append(info)

    pairs, covered = [], []
    for ftype in types:
        models = by_type.get(ftype, [])
        for family in families:
            fitting = [mid for mid, styles in models if family in styles or C.NEUTRAL in styles]
            if fitting:
                covered.append({"type": ftype, "family": family, "count": len(fitting), "models": fitting[:5]})
                continue
            if models:
                seen = sorted({s for _mid, styles in models for s in styles})
                reason = (f"no usable {ftype} model lists '{family}' or '{C.NEUTRAL}' ({len(models)} usable {ftype} "
                          f"model{'s' if len(models) != 1 else ''}; their styles: {', '.join(seen)})")
            else:
                reason = f"no usable {ftype} model in the catalogues"
            skipped = skipped_by_type.get(ftype)
            if skipped:
                reason += "; not counted: " + ", ".join(f"{n} {why}" for why, n in sorted(skipped.items()))
            seeds = [seed_for(ftype, family, i, cfg.get("seed_base", 0)) for i in range(1, n_images + 1)]
            pairs.append({"pair": pair_id(ftype, family), "type": ftype, "family": family,
                          "prompt": prompt_for(ftype, family, cfg), "seeds": seeds, "reason": reason})
    doc = {
        "schema_version": SCHEMA_VERSION, "kind": "generate_plan", "generated_utc": now_utc(),
        "rules": "docs/milestone8.md §3", "families": list(families), "types": types,
        "excluded_types": list(cfg.get("exclude_types") or []), "images_per_pair": n_images,
        "config_sha256": config_sha256(cfg), "catalogs": sources,
        "counts": {"pairs": len(pairs), "covered": len(covered), "total": len(types) * len(families)},
        "pairs": pairs, "covered": covered,
    }
    path = write_json(out / GEN_DIR / PLAN_NAME, doc)
    log(f"generate plan: {len(pairs)} of {len(types) * len(families)} (type, family) pairs need a model "
        f"({len(families)} families, {len(types)} types; {len(covered)} covered) -> {path}")
    return doc


# --------------------------------------------------------------------------
# Target plan (Milestone 9, docs/milestone9.md §2.3)
# --------------------------------------------------------------------------

def record_type(rec: dict) -> Optional[str]:
    """The type a record counts for: ``decor_type`` of a decor record, else ``type``."""
    if (rec.get("kind") or "furniture") == "decor":
        return rec.get("decor_type") or (str(rec.get("type") or "")[len("decor_"):] or None)
    return rec.get("type")


def usable_for_target(rec: dict, fmt: str) -> tuple[bool, str]:
    """``usable`` for furniture and decor alike: accepted, not parametric, with styles, a bed with a mattress or a
    frame."""
    from wenart.furniture import catalog as C
    if fmt == "accepted" and rec.get("accepted") is not True:
        return False, "not accepted"
    if rec.get("parametric"):
        return False, "parametric entry"
    styles = rec.get("styles")
    if not isinstance(styles, list) or not styles:
        return False, "no styles"
    if rec.get("type") in C.BED_TYPES and not (rec.get("has_mattress") is True or rec.get("bed_frame") is True):
        return False, "bed without a mattress and not a bed frame"
    return True, ""


def existing_items(out: Path) -> dict[str, dict[int, dict]]:
    """``{pair: {index: {type, family, prompt, seed}}}`` of every image an earlier run rendered (the image JSONs in
    ``<out>/generate/<pair>/``): a target plan keeps them (their models stay in the survey) and numbers its new
    images after them."""
    found: dict[str, dict[int, dict]] = {}
    gen = Path(out) / GEN_DIR
    if not gen.is_dir():
        return found
    for folder in sorted(p for p in gen.iterdir() if p.is_dir()):
        for f in sorted(folder.glob("img_*.json")):
            meta = read_json(f)
            if not isinstance(meta, dict) or meta.get("index") is None or not meta.get("type"):
                continue
            found.setdefault(folder.name, {})[int(meta["index"])] = {
                "type": meta["type"], "family": meta.get("family"), "prompt": meta.get("prompt"),
                "seed": meta.get("seed")}
    return found


def make_target_plan(catalogs: list[Path], families: list[str], out: Path, cfg: Optional[dict] = None,
                     target: int = 20, types: Optional[list[str]] = None, rate: Optional[float] = None,
                     log: Callable = log_print) -> dict:
    """The new candidates that bring every type to ``target`` accepted models -> ``<out>/generate/plan.json``
    (``mode: target``; docs/milestone9.md §2.3).

    Per type: ``deficit = target - accepted`` (usable records of the catalogues, every source), ``ceil(deficit /
    rate)`` new candidates (``rate``: ``generate.yaml target_accept_rate``, 0.7), round robin over ``families``
    ordered by the type's fitting models (fewest first; a ``neutral`` model fits every family), each a new image
    index of its (type, family) pair after the indexes earlier runs used. ``order``: round by round (the n-th new
    candidate of every type; types with the larger deficit first), then the earlier runs' items (done: kept in the
    survey, never redone)."""
    from wenart.furniture import catalog as C
    cfg = cfg or load_config()
    out = Path(out)
    target = int(target)
    if target < 1:
        raise UsageError("--target must be at least 1")
    rate = float(rate or cfg.get("target_accept_rate") or 0.7)
    if not 0.0 < rate <= 1.0:
        raise UsageError("the acceptance rate must be in (0, 1]")
    types = list(types) if types else target_types(cfg)
    sources, models = [], {t: [] for t in types}
    for path in catalogs:
        fmt, records = read_catalog(path)
        info = {"path": str(path), "format": fmt, "sha256": sha256_file(path), "records": len(records), "usable": 0,
                "skipped": {}}
        for rec in records:
            ftype = record_type(rec)
            if ftype not in models:
                continue
            ok, reason = usable_for_target(rec, fmt)
            if not ok:
                info["skipped"][reason] = info["skipped"].get(reason, 0) + 1
                continue
            info["usable"] += 1
            models[ftype].append((record_id(rec), [str(s) for s in rec["styles"]]))
        sources.append(info)
    earlier = existing_items(out)
    used = {pair: max(idx) for pair, idx in earlier.items() if idx}
    per_type, deficits = {}, {}
    for ftype in types:
        have = models[ftype]
        deficit = target - len(have)
        fitting = {f: sum(1 for _m, st in have if f in st or C.NEUTRAL in st) for f in families}
        entry = {"type": ftype, "accepted": len(have), "deficit": max(0, deficit), "new": 0,
                 "fitting_by_family": fitting}
        if deficit > 0:
            n_new = int(math.ceil(deficit / rate))
            order = sorted(families, key=lambda f: (fitting[f], families.index(f)))
            entry["new"] = n_new
            entry["families"] = [order[i % len(order)] for i in range(n_new)]
            deficits[ftype] = deficit
        per_type[ftype] = entry
    pairs: dict[str, dict] = {}

    def pair_entry(ftype: str, family: str) -> dict:
        pid = pair_id(ftype, family)
        if pid not in pairs:
            pairs[pid] = {"pair": pid, "type": ftype, "family": family, "prompt": prompt_for(ftype, family, cfg),
                          "items": [], "new": 0, "earlier": 0}
        return pairs[pid]

    order, new_by_type = [], {t: [] for t in deficits}
    for ftype in sorted(deficits, key=lambda t: (-deficits[t], types.index(t))):
        for family in per_type[ftype]["families"]:
            p = pair_entry(ftype, family)
            pid = p["pair"]
            used[pid] = used.get(pid, 0) + 1
            index = used[pid]
            p["items"].append({"index": index, "seed": seed_for(ftype, family, index, cfg.get("seed_base", 0)),
                               "prompt": p["prompt"]})
            p["new"] += 1
            new_by_type[ftype].append([pid, index])
    for rnd in range(max((len(v) for v in new_by_type.values()), default=0)):
        for ftype in sorted(deficits, key=lambda t: (-deficits[t], types.index(t))):
            if rnd < len(new_by_type[ftype]):
                order.append(new_by_type[ftype][rnd])
    known = set(known_families())
    for pid, idx in sorted(earlier.items()):
        for index, meta in sorted(idx.items()):
            ftype, family = meta["type"], meta.get("family")
            if ftype not in (cfg.get("type_words") or {}) or family not in known or ftype not in target_types(cfg):
                continue
            p = pair_entry(ftype, family)
            if any(int(it["index"]) == index for it in p["items"]):
                continue
            p["items"].append({"index": index, "seed": meta.get("seed"), "prompt": meta.get("prompt") or p["prompt"]})
            p["earlier"] += 1
            order.append([pid, index])
    for p in pairs.values():
        p["items"].sort(key=lambda it: int(it["index"]))
        p["seeds"] = [it["seed"] for it in p["items"]]
        p["reason"] = (f"{per_type[p['type']]['accepted']} accepted {p['type']} model(s), target {target}"
                       if p["type"] in per_type else "earlier generated images")
    n_new = sum(p["new"] for p in pairs.values())
    doc = {
        "schema_version": SCHEMA_VERSION, "kind": "generate_plan", "mode": "target", "generated_utc": now_utc(),
        "rules": "docs/milestone9.md §2.3", "families": list(families), "types": types, "target": target,
        "accept_rate": rate, "excluded_types": list(cfg.get("exclude_types") or []), "config_sha256": config_sha256(cfg),
        "catalogs": sources, "per_type": per_type,
        "counts": {"pairs": len(pairs), "new_items": n_new, "earlier_items": sum(p["earlier"] for p in pairs.values()),
                   "types_short": len(deficits), "total_deficit": sum(deficits.values())},
        "pairs": [pairs[k] for k in sorted(pairs)], "order": order,
    }
    path = write_json(out / GEN_DIR / PLAN_NAME, doc)
    log(f"generate plan (target {target}): {len(deficits)} of {len(types)} types short by {sum(deficits.values())} "
        f"model(s) in all; {n_new} new candidates at an acceptance rate of {rate:g}, "
        f"{doc['counts']['earlier_items']} earlier items kept -> {path}")
    return doc


# --------------------------------------------------------------------------
# Items, keys and records
# --------------------------------------------------------------------------

def read_plan(path: Path) -> dict:
    doc = read_json(Path(path)) if Path(path).is_file() else None
    if not isinstance(doc, dict) or not isinstance(doc.get("pairs"), list):
        raise UsageError(f"plan {path} not found or not a generate plan (python -m wenart.assets.generate plan)")
    return doc


def plan_items(plan: dict, cfg: dict, images_per_pair: Optional[int] = None) -> list[dict]:
    """Every (pair, image index) of the plan, ordered index-major (image 1 of every pair first). A target plan
    (Milestone 9, ``mode: target``) lists its items per pair (``items``: index, seed, prompt) and their order
    (``order``: [pair, index] pairs, the new items round by round, then the items of earlier runs)."""
    if plan.get("mode") == "target":
        return target_plan_items(plan, cfg)
    n_images = int(images_per_pair or plan.get("images_per_pair") or cfg.get("images_per_pair") or 2)
    if n_images < 1:
        raise UsageError("--images-per-pair must be at least 1")
    known = set(known_families())
    items = []
    for index in range(1, n_images + 1):
        for p in plan["pairs"]:
            ftype, family = p.get("type"), p.get("family")
            if ftype not in (cfg.get("type_words") or {}) or family not in known:
                raise UsageError(f"plan pair {p.get('pair')!r}: unknown type {ftype!r} or family {family!r}")
            seeds = p.get("seeds") or []
            seed = int(seeds[index - 1]) if index <= len(seeds) else seed_for(ftype, family, index,
                                                                              cfg.get("seed_base", 0))
            items.append({"pair": p.get("pair") or pair_id(ftype, family), "type": ftype, "family": family,
                          "index": index, "prompt": p.get("prompt") or prompt_for(ftype, family, cfg), "seed": seed})
    return items


def target_plan_items(plan: dict, cfg: dict) -> list[dict]:
    """The items of a target plan in its ``order`` (every listed item once; unknown types or families: UsageError)."""
    known = set(known_families())
    allowed = set(target_types(cfg))
    by_key: dict[tuple, dict] = {}
    for p in plan["pairs"]:
        ftype, family = p.get("type"), p.get("family")
        if ftype not in allowed or ftype not in (cfg.get("type_words") or {}) or family not in known:
            raise UsageError(f"plan pair {p.get('pair')!r}: unknown type {ftype!r} or family {family!r}")
        pair = p.get("pair") or pair_id(ftype, family)
        for it in p.get("items") or []:
            index = int(it["index"])
            by_key[(pair, index)] = {"pair": pair, "type": ftype, "family": family, "index": index,
                                     "prompt": it.get("prompt") or prompt_for(ftype, family, cfg),
                                     "seed": int(it["seed"]) if it.get("seed") is not None else
                                     seed_for(ftype, family, index, cfg.get("seed_base", 0))}
    items, seen = [], set()
    for pair, index in plan.get("order") or sorted(by_key):
        key = (str(pair), int(index))
        if key in by_key and key not in seen:
            items.append(by_key[key])
            seen.add(key)
    items += [by_key[k] for k in sorted(by_key) if k not in seen]
    return items


def item_paths(out: Path, item: dict) -> dict[str, Path]:
    d = Path(out) / GEN_DIR / item["pair"]
    n = item["index"]
    return {"dir": d, "png": d / f"img_{n}.png", "img_json": d / f"img_{n}.json",
            "glb": d / f"model_{n}.glb", "glb_json": d / f"model_{n}.json"}


def model_ref(cfg: dict, key: str) -> str:
    m = cfg["models"][key]
    return f"{m['repo']}@{m['revision']}"


def image_key(item: dict, cfg: dict) -> str:
    return canonical_sha256({"code": CODE_VERSION, "step": "image", "prompt": item["prompt"], "seed": item["seed"],
                             "model": model_ref(cfg, "zimage"), "settings": cfg["image"]})


def mesh_settings(cfg: dict, item: Optional[dict] = None) -> dict:
    """The TRELLIS.2 settings that change the output (not the memory mode); a decor item (Milestone 9) takes the
    ``trellis_decor`` overrides (small objects: the 512 pipeline, smaller textures). Furniture keeps the M8 settings
    (and so its M8 keys)."""
    out = {k: v for k, v in cfg["trellis"].items() if k != "resident_min_vram_gib"}
    if item is not None and item.get("type") in decor_types(cfg):
        out.update(cfg.get("trellis_decor") or {})
    return out


def mesh_key(item: dict, image_sha256: str, cfg: dict) -> str:
    return canonical_sha256({
        "code": CODE_VERSION, "step": "mesh", "image_sha256": image_sha256, "seed": item["seed"],
        "models": {k: model_ref(cfg, k) for k in ("trellis", "ss_decoder", "dinov3", "rembg")},
        "trellis_code": cfg["trellis_code"]["commit"], "settings": mesh_settings(cfg, item)})


def image_state(out: Path, item: dict, cfg: dict) -> Optional[str]:
    """The PNG's sha256 when the image is done with the current key, else None."""
    p = item_paths(out, item)
    meta = read_json(p["img_json"]) if p["img_json"].is_file() else None
    if not meta or meta.get("key") != image_key(item, cfg) or not p["png"].is_file():
        return None
    sha = sha256_file(p["png"])
    return sha if sha == meta.get("image_sha256") else None


def mesh_state(out: Path, item: dict, image_sha256: str, cfg: dict) -> tuple[str, Optional[dict]]:
    """``("done", meta)``, ``("failed", meta)`` (same key) or ``("todo", None)``."""
    p = item_paths(out, item)
    meta = read_json(p["glb_json"]) if p["glb_json"].is_file() else None
    if not meta or meta.get("key") != mesh_key(item, image_sha256, cfg):
        return "todo", None
    if meta.get("status") == "failed":
        return "failed", meta
    if meta.get("status") == "ok" and p["glb"].is_file() and sha256_file(p["glb"]) == meta.get("glb_sha256"):
        return "done", meta
    return "todo", None


def glb_face_count(path: Path) -> int:
    """Triangles of every mesh primitive in the GLB JSON (indices, else positions; strips and fans counted)."""
    doc = glb_json(path)
    accessors = doc.get("accessors") or []
    total = 0
    for mesh in doc.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            ref = prim.get("indices")
            if ref is None:
                ref = (prim.get("attributes") or {}).get("POSITION")
            if ref is None or ref >= len(accessors):
                continue
            count = int(accessors[ref].get("count") or 0)
            mode = prim.get("mode", 4)
            if mode == 4:
                total += count // 3
            elif mode in (5, 6):
                total += max(count - 2, 0)
    return total


def survey_record(out: Path, item: dict, meta: dict, cfg: dict, rank: int) -> dict:
    """One candidate in the ``survey.json`` record shape plus the milestone 8 fields."""
    p = item_paths(out, item)
    info = meta["glb_info"]
    rec_cfg = cfg["record"]
    zi, tr = cfg["models"]["zimage"], cfg["models"]["trellis"]
    return {
        "uid": uid_for(item["type"], item["family"], item["index"], meta["glb_sha256"]),
        "group": item["type"], "types": [item["type"]], "categories": [],
        "title": f"Generated {item['family']} {item['type'].replace('_', ' ')} ({item['index']})",
        "author": rec_cfg["author"], "source_url": rec_cfg["source_url"],
        "licence": rec_cfg["licence"], "licence_raw": rec_cfg["licence_raw"],
        "face_count": int(meta["face_count"]), "glb_size_meta": None, "texture_count": int(info.get("textures") or 0),
        "likes": 0, "views": 0, "prefer_hit": False,
        "object_path": p["glb"].relative_to(Path(out)).as_posix(), "rank": rank,
        "glb": str(p["glb"].resolve()), "glb_sha256": meta["glb_sha256"], "glb_bytes": int(meta["glb_bytes"]),
        "glb_info": info,
        "source": SOURCE, "licence_flag": None, "units_known": False,
        "kind": "decor" if item["type"] in decor_types(cfg) else "furniture",
        "decor_type": item["type"] if item["type"] in decor_types(cfg) else None,
        "style_hint": item["family"],
        "generated": {"prompt": item["prompt"], "image_sha256": meta["image_sha256"], "model": tr["repo"],
                      "revision": tr["revision"], "seed": item["seed"]},
        "generation": {"pair": item["pair"], "index": item["index"],
                       "image": p["png"].relative_to(Path(out)).as_posix(), "image_model": zi["repo"],
                       "image_revision": zi["revision"], "trellis_code": cfg["trellis_code"]["commit"],
                       "settings": mesh_settings(cfg, item), "image_settings": cfg["image"],
                       "seconds": meta.get("seconds"), "versions": meta.get("versions")},
    }


def build_survey(out: Path, plan: dict, cfg: dict, images_per_pair: Optional[int] = None,
                 plan_path: Optional[Path] = None, cut: bool = False, errors: Optional[list[str]] = None) -> dict:
    """``<out>/survey_generated.json`` from the item files of the plan (only items with the current keys)."""
    out = Path(out)
    items = plan_items(plan, cfg, images_per_pair)
    family_order = {f: i for i, f in enumerate(plan.get("families") or known_families())}
    done, refused = [], []
    counts: dict[str, dict] = {}
    seen_pairs: set = set()
    for item in items:
        c = counts.setdefault(item["type"], {"pairs": 0, "items": 0, "images": 0, "models": 0, "failed": 0,
                                             "not_generated": 0})
        c["items"] += 1
        if item["pair"] not in seen_pairs:
            seen_pairs.add(item["pair"])
            c["pairs"] += 1
        sha = image_state(out, item, cfg)
        base = {"pair": item["pair"], "type": item["type"], "family": item["family"], "index": item["index"]}
        if sha is None:
            c["not_generated"] += 1
            refused.append({**base, "code": "not_generated", "detail": "no image (not reached or cut)"})
            continue
        c["images"] += 1
        state, meta = mesh_state(out, item, sha, cfg)
        if state == "done":
            done.append((item, meta))
            c["models"] += 1
        elif state == "failed":
            c["failed"] += 1
            refused.append({**base, "code": meta.get("code") or "generation_failed", "detail": meta.get("error")})
        else:
            c["not_generated"] += 1
            refused.append({**base, "code": "not_generated", "detail": "no model (not reached or cut)"})
    done.sort(key=lambda im: (im[0]["type"], family_order.get(im[0]["family"], 99), im[0]["index"]))
    candidates, rank = [], {}
    for item, meta in done:
        rank[item["type"]] = rank.get(item["type"], 0) + 1
        candidates.append(survey_record(out, item, meta, cfg, rank[item["type"]]))
    refused_counts: dict[str, int] = {}
    for r in refused:
        refused_counts[r["code"]] = refused_counts.get(r["code"], 0) + 1
    models = {k: {f: m[f] for f in ("repo", "revision", "licence") if f in m} for k, m in cfg["models"].items()}
    doc = {
        "schema_version": SCHEMA_VERSION, "kind": "generated_survey", "generated_utc": now_utc(), "source": SOURCE,
        "rules": "docs/milestone8.md §3" + (", docs/milestone9.md §2.3" if plan.get("mode") == "target" else ""),
        "models": models, "trellis_code": cfg["trellis_code"],
        "plan": {"path": str(plan_path) if plan_path else None,
                 "sha256": sha256_file(plan_path) if plan_path and Path(plan_path).is_file() else None,
                 "pairs": len(plan["pairs"]), "families": plan.get("families")},
        "images_per_pair": max((i["index"] for i in items), default=0), "config_sha256": config_sha256(cfg),
        "complete": not cut and not refused, "cut_by_deadline": bool(cut), "errors": list(errors or []),
        "counts": counts, "refused_counts": dict(sorted(refused_counts.items())),
        "candidates": candidates, "refused": refused,
    }
    write_json(out / SURVEY_NAME, doc)
    return doc


# --------------------------------------------------------------------------
# Run (GPU through the backends; fakes in the CPU tests)
# --------------------------------------------------------------------------

def _save_png(array, path: Path) -> None:
    from PIL import Image
    import numpy as np
    arr = np.ascontiguousarray(np.asarray(array, dtype=np.uint8)[:, :, :3])
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    Image.fromarray(arr).save(tmp, format="PNG")
    tmp.replace(path)


class _Timer:
    """Measured seconds per kind of work; the config estimate until the first measurement."""

    def __init__(self, cfg: dict):
        self.est = dict(cfg.get("estimate_seconds") or {})
        self.seen: dict[str, list[float]] = {}

    def add(self, kind: str, seconds: float) -> None:
        self.seen.setdefault(kind, []).append(float(seconds))

    def expect(self, kind: str) -> float:
        vals = self.seen.get(kind)
        return sum(vals) / len(vals) if vals else float(self.est.get(kind, 60))


def parse_shard(text: Optional[str]) -> tuple[int, int]:
    """``"I/N"`` -> ``(I, N)`` with 0 <= I < N (Milestone 9: N workers share one GPU, each takes every N-th item of
    the plan order); None -> ``(0, 1)``."""
    if text is None or str(text).strip() == "":
        return 0, 1
    try:
        i, n = (int(v) for v in str(text).split("/"))
    except ValueError:
        raise UsageError(f"--shard {text!r} is not I/N") from None
    if n < 1 or not 0 <= i < n:
        raise UsageError(f"--shard {text!r}: need 0 <= I < N")
    return i, n


def run(out: Path, plan_path: Path, *, images_per_pair: Optional[int] = None, deadline: Optional[float] = None,
        cfg: Optional[dict] = None, retry_failed: bool = False, image_backend: Optional[Callable] = None,
        mesh_backend: Optional[Callable] = None, clock: Callable[[], float] = time.time,
        log: Callable = log_print, shard: tuple[int, int] = (0, 1)) -> int:
    """Phase A (images), phase B (models), then the survey; see the module docstring. Returns the exit code.
    ``shard`` (Milestone 9): ``(i, n)`` takes every n-th item of the plan order from the i-th on, so n workers
    share the GPU; each writes the survey of the whole plan at its end (the prep job writes it once more after
    all of them)."""
    cfg = cfg or load_config()
    out = Path(out)
    plan = read_plan(plan_path)
    items = plan_items(plan, cfg, images_per_pair)
    shard_k, shard_n = shard
    if shard_n > 1:
        items = [it for j, it in enumerate(items) if j % shard_n == shard_k]
        log(f"generate run: shard {shard_k}/{shard_n}: {len(items)} items")
    image_backend = image_backend or ZImageText2Image
    mesh_backend = mesh_backend or TrellisImageTo3D
    timer = _Timer(cfg)
    cut, errors, load_failed = False, [], False

    def over(kind: str, extra: str = "") -> bool:
        if deadline is None:
            return False
        need = timer.expect(kind) + (timer.expect(extra) if extra else 0.0)
        return clock() + need > deadline

    # Phase A: images (Z-Image-Turbo loaded once, freed before TRELLIS.2 loads).
    todo = [it for it in items if image_state(out, it, cfg) is None]
    log(f"generate run: {len(plan['pairs'])} pairs, {len(items)} items; {len(todo)} images to render")
    if todo and over("image_load", "image"):
        cut = True
        log("generate run: the deadline leaves no time to load Z-Image-Turbo")
    elif todo:
        backend = _load_backend(image_backend, cfg, timer, "image_load", clock, errors, "Z-Image-Turbo", log)
        load_failed |= backend is None
        if backend is not None:
            try:
                for n, item in enumerate(todo, 1):
                    if over("image"):
                        cut = True
                        log(f"generate run: deadline: {len(todo) - n + 1} images left")
                        break
                    _one_image(out, item, cfg, backend, timer, clock, errors, log, f"{n}/{len(todo)}")
            finally:
                backend.close()

    # Phase B: models (TRELLIS.2 loaded once).
    pending = []
    for item in items:
        sha = image_state(out, item, cfg)
        if sha is None:
            continue
        state, _meta = mesh_state(out, item, sha, cfg)
        if state == "todo" or (state == "failed" and retry_failed):
            pending.append((item, sha))
    log(f"generate run: {len(pending)} models to generate")
    if pending and not cut and over("mesh_load", "mesh"):
        cut = True
        log("generate run: the deadline leaves no time to load TRELLIS.2")
    elif pending and not cut:
        backend = _load_backend(mesh_backend, cfg, timer, "mesh_load", clock, errors, "TRELLIS.2", log)
        load_failed |= backend is None
        if backend is not None:
            try:
                for n, (item, sha) in enumerate(pending, 1):
                    if over("mesh"):
                        cut = True
                        log(f"generate run: deadline: {len(pending) - n + 1} models left")
                        break
                    _one_mesh(out, item, sha, cfg, backend, timer, clock, log, f"{n}/{len(pending)}")
            finally:
                backend.close()

    if shard_n > 1:
        # A shard leaves the survey to the prep job (one write after every worker; never two writers at once).
        n_cand = 0
        for item in items:
            sha = image_state(out, item, cfg)
            if sha is not None and mesh_state(out, item, sha, cfg)[0] == "done":
                n_cand += 1
        log(f"generate run: shard {shard_k}/{shard_n}: {n_cand} of {len(items)} models done"
            + (" (cut by the deadline)" if cut else "") + (f"; errors: {errors}" if errors else ""))
    else:
        survey = build_survey(out, plan, cfg, images_per_pair, plan_path, cut=cut, errors=errors)
        n_cand = len(survey["candidates"])
        log(f"generate run: {n_cand} generated candidates -> {out / SURVEY_NAME}"
            + (" (cut by the deadline)" if cut else "") + (f"; errors: {errors}" if errors else ""))
    if cut:
        return EXIT_DEADLINE
    if items and (load_failed or n_cand == 0):
        return EXIT_FAIL
    return EXIT_OK


def _load_backend(factory: Callable, cfg: dict, timer: "_Timer", kind: str, clock, errors: list, name: str, log):
    """``factory(cfg).load()`` timed; None (and the reason in ``errors``) when it fails."""
    backend = None
    t0 = clock()
    try:
        backend = factory(cfg)
        backend.load()
    except Exception as exc:  # noqa: BLE001 - recorded; the run exits 1
        errors.append(f"{name} did not load: {type(exc).__name__}: {exc}")
        log(f"generate run: {name} did not load: {type(exc).__name__}: {exc}")
        if backend is not None:
            backend.close()
        return None
    timer.add(kind, clock() - t0)
    return backend


def _one_image(out: Path, item: dict, cfg: dict, backend, timer: "_Timer", clock, errors: list, log,
               tag: str) -> None:
    """One Z-Image-Turbo image: PNG written atomically, then its JSON (key, sha256); a failure is logged and the
    item stays not generated."""
    p = item_paths(out, item)
    t0 = clock()
    try:
        arr = backend.text_to_image(item["prompt"], item["seed"])
        _save_png(arr, p["png"])
    except Exception as exc:  # noqa: BLE001 - one failed image never stops the others
        errors.append(f"image {item['pair']} #{item['index']}: {type(exc).__name__}: {exc}")
        log(f"generate run: image {item['pair']} #{item['index']} ({tag}) FAILED: {type(exc).__name__}: {exc}")
        free = getattr(backend, "free", None)
        if callable(free):
            free()
        return
    seconds = clock() - t0
    timer.add("image", seconds)
    write_json(p["img_json"], {
        "key": image_key(item, cfg), "pair": item["pair"], "type": item["type"], "family": item["family"],
        "index": item["index"], "prompt": item["prompt"], "seed": item["seed"], "model": model_ref(cfg, "zimage"),
        "settings": cfg["image"], "image_sha256": sha256_file(p["png"]), "seconds": round(seconds, 2),
        "versions": _versions(backend), "generated_utc": now_utc()})
    log(f"generate run: image {item['pair']} #{item['index']} ({tag}) in {seconds:.1f} s")


def _versions(backend) -> Optional[dict]:
    fn = getattr(backend, "versions", None)
    try:
        return fn() if callable(fn) else None
    except Exception:  # noqa: BLE001 - informative only
        return None


def _one_mesh(out: Path, item: dict, image_sha: str, cfg: dict, backend, timer: _Timer, clock, log, tag: str) -> None:
    """One TRELLIS.2 model: GLB written atomically, checked (faces, texture), its JSON written (ok or failed)."""
    p = item_paths(out, item)
    tmp = p["glb"].with_name(p["glb"].name + ".tmp")
    base = {"key": mesh_key(item, image_sha, cfg), "pair": item["pair"], "type": item["type"],
            "family": item["family"], "index": item["index"], "seed": item["seed"], "prompt": item["prompt"],
            "image_sha256": image_sha, "models": {k: model_ref(cfg, k) for k in ("trellis", "ss_decoder", "dinov3",
                                                                                 "rembg")},
            "trellis_code": cfg["trellis_code"]["commit"], "settings": mesh_settings(cfg, item),
            "generated_utc": now_utc()}
    t0 = clock()
    try:
        extra = {}
        if mesh_settings(cfg, item) != mesh_settings(cfg):
            extra["settings"] = mesh_settings(cfg, item)          # Milestone 9 decor: the trellis_decor overrides
        meta = backend.image_to_glb(p["png"], tmp, item["seed"], **extra) or {}
        info = glb_info(tmp)
        faces = glb_face_count(tmp)
        if faces < 1:
            raise _Refused("no_faces", "the exported GLB has no triangles")
        if not info.get("textured"):
            raise _Refused("untextured", f"{info.get('images')} images, {info.get('textures')} textures")
        tmp.replace(p["glb"])
        seconds = clock() - t0
        timer.add("mesh", seconds)
        write_json(p["glb_json"], {**base, "status": "ok", "code": None, "error": None, "glb": p["glb"].name,
                                   "glb_sha256": sha256_file(p["glb"]), "glb_bytes": p["glb"].stat().st_size,
                                   "face_count": faces, "glb_info": info, "seconds": round(seconds, 2),
                                   "backend": meta, "versions": _versions(backend)})
        log(f"generate run: model {item['pair']} #{item['index']} ({tag}): {faces} faces in {seconds:.1f} s")
    except Exception as exc:  # noqa: BLE001 - one failed object never stops the others
        seconds = clock() - t0
        timer.add("mesh", seconds)
        code = exc.code if isinstance(exc, _Refused) else "generation_failed"
        detail = exc.detail if isinstance(exc, _Refused) else f"{type(exc).__name__}: {exc}"
        if tmp.exists():
            tmp.unlink()
        write_json(p["glb_json"], {**base, "status": "failed", "code": code, "error": detail,
                                   "seconds": round(seconds, 2), "versions": _versions(backend)})
        log(f"generate run: model {item['pair']} #{item['index']} ({tag}) FAILED: {detail}")
        free = getattr(backend, "free", None)
        if callable(free):
            free()


class _Refused(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail = code, detail


# --------------------------------------------------------------------------
# GPU backends (lazy imports: torch, transformers, diffusers, trellis2, o_voxel)
# --------------------------------------------------------------------------

def _free_cuda() -> None:
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


def to_uint8(image):
    """Pipeline ``output_type="np"`` image (float 0..1) -> uint8, rounded as diffusers' numpy_to_pil."""
    import numpy as np
    a = np.asarray(image, dtype=np.float32)
    return np.clip(np.rint(a * 255.0), 0, 255).astype(np.uint8)


def text_classes(base_dir: Path) -> tuple[str, str]:
    """transformers class names of the tokenizer and the text encoder (``model_index.json``)."""
    index = json.loads((Path(base_dir) / "model_index.json").read_text(encoding="utf-8"))
    tok, enc = index["tokenizer"], index["text_encoder"]
    if tok[0] != "transformers" or enc[0] != "transformers":
        raise ValueError(f"unexpected tokenizer/text encoder libraries in model_index.json: {tok}, {enc}")
    return tok[1], enc[1]


class ZImageText2Image:
    """Z-Image-Turbo text-to-image (diffusers 0.40.0 ``ZImagePipeline``) from the pinned local snapshot.

    Built from its parts like the polish backend (``wenart.polish.zimage``): tokenizer and text encoder from the
    snapshot's local folders (no hub lookups, so ``HF_HUB_OFFLINE=1`` works), transformer and VAE in bf16 on the GPU,
    the snapshot's FlowMatchEulerDiscreteScheduler. About 21 GB of VRAM, freed by ``close()``."""

    def __init__(self, cfg: dict, device: str = "cuda"):
        os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", ALLOC_CONF)
        self.cfg, self.device, self.pipe = cfg, device, None

    def load(self) -> None:
        import torch
        import transformers
        from diffusers import AutoencoderKL, FlowMatchEulerDiscreteScheduler, ZImagePipeline, ZImageTransformer2DModel

        from wenart.hfcache import local_snapshot
        m = self.cfg["models"]["zimage"]
        base = local_snapshot(m["repo"], m["revision"], m.get("allow_patterns"))
        tok_cls, enc_cls = text_classes(base)
        tokenizer = getattr(transformers, tok_cls).from_pretrained(str(base / "tokenizer"))
        encoder = getattr(transformers, enc_cls).from_pretrained(str(base / "text_encoder"), dtype=torch.bfloat16,
                                                                 device_map=self.device)
        transformer = ZImageTransformer2DModel.from_pretrained(str(base), subfolder="transformer",
                                                               dtype=torch.bfloat16, device_map=self.device)
        vae = AutoencoderKL.from_pretrained(str(base), subfolder="vae", dtype=torch.bfloat16).to(self.device)
        scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(str(base), subfolder="scheduler")
        self.pipe = ZImagePipeline(scheduler=scheduler, vae=vae, text_encoder=encoder, tokenizer=tokenizer,
                                   transformer=transformer)
        self.pipe.set_progress_bar_config(disable=True)

    def text_to_image(self, prompt: str, seed: int):
        import torch
        im = self.cfg["image"]
        g = torch.Generator("cpu").manual_seed(int(seed))
        out = self.pipe(prompt=prompt, height=int(im["size"]), width=int(im["size"]),
                        num_inference_steps=int(im["steps"]), guidance_scale=float(im["guidance_scale"]),
                        generator=g, output_type="np")
        return to_uint8(out.images[0])

    def versions(self) -> dict:
        import diffusers
        import torch
        import transformers
        return {"torch": torch.__version__, "diffusers": diffusers.__version__,
                "transformers": transformers.__version__,
                "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"}

    def free(self) -> None:
        _free_cuda()

    def close(self) -> None:
        self.pipe = None
        _free_cuda()


def trellis_env() -> dict:
    """``trellis_env.json`` of venv-trellis (attention backend, source folder, commit; scripts/pod_setup_trellis.sh),
    from ``WENART_TRELLIS_ENV`` or ``<sys.prefix>/trellis_env.json``; empty when absent."""
    path = Path(os.environ.get("WENART_TRELLIS_ENV") or Path(sys.prefix) / TRELLIS_ENV_NAME)
    return (read_json(path) or {}) if path.is_file() else {}


def pipeline_args(doc: dict, cfg: dict, dinov3_dir: str, rembg_dir: str) -> tuple[dict, dict]:
    """``pipeline.json`` of the pinned TRELLIS.2-4B with every part read from a local folder.

    Returns ``(doc, links)``: the patched document (model paths relative to the folder that will hold it, image
    condition model and background remover as local folders) and ``{link name: repo key}`` for the symlinks the
    folder needs (``ckpts`` -> the TRELLIS.2 snapshot's ckpts, ``ss_decoder`` -> the TRELLIS v1 snapshot). Refuses a
    ``pipeline.json`` whose names differ from the ones checked for this revision (never a silent change)."""
    if doc.get("name") != "Trellis2ImageTo3DPipeline":
        raise ValueError(f"pipeline.json names {doc.get('name')!r}, expected Trellis2ImageTo3DPipeline")
    out = json.loads(json.dumps(doc))
    args = out["args"]
    m = cfg["models"]
    ss_prefix = m["ss_decoder"]["repo"] + "/"
    models, links = {}, {}
    for name, rel in args["models"].items():
        if rel.startswith(ss_prefix):
            models[name] = "ss_decoder/" + rel[len(ss_prefix):]
            links["ss_decoder"] = "ss_decoder"
        elif rel.startswith("ckpts/"):
            models[name] = rel
            links["ckpts"] = "trellis"
        else:
            raise ValueError(f"pipeline.json model {name} -> {rel!r}: neither ckpts/ nor {ss_prefix}")
    args["models"] = models
    cond, rembg = args.get("image_cond_model") or {}, args.get("rembg_model") or {}
    if cond.get("name") != "DinoV3FeatureExtractor" or cond.get("args", {}).get("model_name") != m["dinov3"]["repo"]:
        raise ValueError(f"pipeline.json image_cond_model {cond} is not DinoV3FeatureExtractor({m['dinov3']['repo']})")
    expected = {m["rembg"].get("replaces"), m["rembg"]["repo"]} - {None}
    if rembg.get("name") != "BiRefNet" or rembg.get("args", {}).get("model_name") not in expected:
        raise ValueError(f"pipeline.json rembg_model {rembg} is not BiRefNet({' or '.join(sorted(expected))})")
    cond["args"]["model_name"] = str(dinov3_dir)
    rembg["args"]["model_name"] = str(rembg_dir)
    return out, links


def _dinov3_extract_features(self, image):
    """``DinoV3FeatureExtractor.extract_features`` of TRELLIS.2, finding the ViT blocks in ``model.layer``
    (transformers 4.x) or ``model.model.layer`` (transformers 5.x); otherwise the same computation."""
    import torch.nn.functional as F
    m = self.model
    image = image.to(m.embeddings.patch_embeddings.weight.dtype)
    hidden = m.embeddings(image, bool_masked_pos=None)
    position_embeddings = m.rope_embeddings(image)
    layers = m.layer if hasattr(m, "layer") else m.model.layer
    for layer_module in layers:
        hidden = layer_module(hidden, position_embeddings=position_embeddings)
    return F.layer_norm(hidden, hidden.shape[-1:])


class TrellisImageTo3D:
    """TRELLIS.2-4B image-to-3D and GLB export (venv-trellis on the GPU; see the module docstring)."""

    def __init__(self, cfg: dict, device: str = "cuda"):
        os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", ALLOC_CONF)
        self.cfg, self.device = cfg, device
        self.pipe = None
        self.env = trellis_env()
        self.resident: Optional[bool] = None
        self._folder: Optional[tempfile.TemporaryDirectory] = None

    def _environment(self) -> None:
        """Attention backend and FlexGEMM cache of the setup; the TRELLIS.2 source on sys.path (before import)."""
        for key in ("ATTN_BACKEND", "SPARSE_ATTN_BACKEND", "SPARSE_CONV_BACKEND", "FLEX_GEMM_AUTOTUNE_CACHE_PATH"):
            if self.env.get(key):
                os.environ.setdefault(key, str(self.env[key]))
        src = self.env.get("trellis_src")
        if src and src not in sys.path:
            sys.path.insert(0, src)

    def _pipeline_folder(self) -> Path:
        from wenart.hfcache import local_snapshot
        m = self.cfg["models"]
        snaps = {k: local_snapshot(m[k]["repo"], m[k]["revision"], m[k].get("allow_patterns"))
                 for k in ("trellis", "ss_decoder", "dinov3", "rembg")}
        doc = json.loads((snaps["trellis"] / "pipeline.json").read_text(encoding="utf-8"))
        patched, links = pipeline_args(doc, self.cfg, str(snaps["dinov3"]), str(snaps["rembg"]))
        self._folder = tempfile.TemporaryDirectory(prefix="wenart-trellis-")   # symlinks only, on /tmp
        folder = Path(self._folder.name)
        for link, key in links.items():
            target = snaps[key] / "ckpts" if link == "ckpts" else snaps[key]
            (folder / link).symlink_to(target, target_is_directory=True)
        for name, rel in patched["args"]["models"].items():
            for ext in (".json", ".safetensors"):
                if not (folder / f"{rel}{ext}").is_file():
                    raise FileNotFoundError(f"TRELLIS.2 part {name}: {rel}{ext} is not in the pinned snapshots "
                                            "(scripts/pod_setup_trellis.sh part models)")
        (folder / "pipeline.json").write_text(json.dumps(patched, indent=1), encoding="utf-8")
        return folder

    def load(self) -> None:
        self._environment()
        import torch
        from trellis2.modules import image_feature_extractor as IFE
        from trellis2.pipelines import Trellis2ImageTo3DPipeline

        IFE.DinoV3FeatureExtractor.extract_features = _dinov3_extract_features
        pipe = Trellis2ImageTo3DPipeline.from_pretrained(str(self._pipeline_folder()))
        # transformers 5 loads the fp16 BiRefNet checkpoint as fp16; TRELLIS.2 feeds it float32 tensors.
        pipe.rembg_model.model.float()
        total_gib = torch.cuda.get_device_properties(0).total_memory / 2 ** 30
        self.resident = total_gib >= float(self.cfg["trellis"].get("resident_min_vram_gib", 40))
        pipe.low_vram = not self.resident
        pipe.cuda()
        self.pipe = pipe

    def image_to_glb(self, image_path: Path, glb_path: Path, seed: int, settings: Optional[dict] = None) -> dict:
        import o_voxel
        import torch
        from PIL import Image

        t = dict(self.cfg["trellis"], **(settings or {}))
        image = Image.open(image_path).convert("RGB")      # no alpha: TRELLIS.2 runs its background remover
        torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        mesh = self.pipe.run(image, seed=int(seed), pipeline_type=t["pipeline_type"])[0]
        raw_faces = int(mesh.faces.shape[0])
        mesh.simplify(int(t["simplify"]))
        t1 = time.time()
        glb = o_voxel.postprocess.to_glb(
            vertices=mesh.vertices, faces=mesh.faces, attr_volume=mesh.attrs, coords=mesh.coords,
            attr_layout=mesh.layout, voxel_size=mesh.voxel_size, aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            decimation_target=int(t["decimation_target"]), texture_size=int(t["texture_size"]),
            remesh=bool(t["remesh"]), remesh_band=float(t["remesh_band"]), remesh_project=float(t["remesh_project"]),
            verbose=False)
        Path(glb_path).parent.mkdir(parents=True, exist_ok=True)
        glb.export(file_obj=str(glb_path), file_type="glb")
        t2 = time.time()
        peak = round(torch.cuda.max_memory_allocated() / 2 ** 30, 2)
        del mesh, glb
        _free_cuda()
        return {"seconds_generate": round(t1 - t0, 2), "seconds_export": round(t2 - t1, 2), "raw_faces": raw_faces,
                "pipeline_type": t["pipeline_type"], "peak_vram_gib": peak, "resident": self.resident}

    def versions(self) -> dict:
        import torch
        import transformers
        return {"torch": torch.__version__, "cuda": torch.version.cuda, "transformers": transformers.__version__,
                "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
                "attn_backend": os.environ.get("ATTN_BACKEND"), "trellis_commit": self.env.get("trellis_commit"),
                "resident": self.resident}

    def free(self) -> None:
        _free_cuda()

    def close(self) -> None:
        self.pipe = None
        if self._folder is not None:
            self._folder.cleanup()
            self._folder = None
        _free_cuda()


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.assets.generate",
                                     description="Generated furniture with TRELLIS.2 (docs/milestone8.md §3)")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("plan", help="list the (type, family) pairs without an accepted model (CPU)")
    p.add_argument("--catalog", action="append", default=[], help="accepted.json or a catalogue JSON (repeatable, "
                   "comma lists allowed); the Poly Haven catalog.json is always added")
    p.add_argument("--families", required=True, help="comma list of style families, or 'all'")
    p.add_argument("--out", required=True, help="library folder; writes <out>/generate/plan.json")
    p.add_argument("--types", default=None, help="comma list of types (default: every movable type)")
    p.add_argument("--images-per-pair", type=int, default=None)
    p.add_argument("--no-polyhaven", action="store_true", help="leave the Poly Haven catalog.json out")
    p.add_argument("--target", type=int, default=None, help="Milestone 9: plan the candidates that bring every type "
                   "(furniture and the generated decor types) to this many accepted models (default: the M8 gap plan)")
    p.add_argument("--rate", type=float, default=None, help="expected share of generated candidates the judges "
                   "accept (target plans; default generate.yaml target_accept_rate)")
    r = sub.add_parser("run", help="images (Z-Image-Turbo) and models (TRELLIS.2) of a plan (GPU)")
    r.add_argument("--out", required=True)
    r.add_argument("--plan", required=True)
    r.add_argument("--images-per-pair", type=int, default=None)
    r.add_argument("--deadline", type=float, default=None, help="epoch seconds (default: WENART_DEADLINE)")
    r.add_argument("--retry-failed", action="store_true", help="retry models that failed with the same key")
    r.add_argument("--shard", default=None, help="I/N: this worker's share of the plan (N workers on one GPU)")
    s = sub.add_parser("survey", help="rewrite survey_generated.json from the item files (CPU)")
    s.add_argument("--out", required=True)
    s.add_argument("--plan", required=True)
    s.add_argument("--images-per-pair", type=int, default=None)
    return parser.parse_args(argv)


def main(argv=None, image_backend=None, mesh_backend=None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:
        return EXIT_USAGE if exc.code else EXIT_OK
    try:
        cfg = load_config()
        if args.command == "plan":
            catalogs = [Path(c) for c in split_list(args.catalog)]
            if not args.no_polyhaven and POLYHAVEN_CATALOG.resolve() not in {c.resolve() for c in catalogs}:
                catalogs.append(POLYHAVEN_CATALOG)
            if args.target is not None:
                make_target_plan(catalogs, parse_families(args.families), Path(args.out), cfg, target=args.target,
                                 types=parse_types(args.types, cfg, target=True), rate=args.rate)
                return EXIT_OK
            make_plan(catalogs, parse_families(args.families), Path(args.out), cfg,
                      types=parse_types(args.types, cfg), images_per_pair=args.images_per_pair)
            return EXIT_OK
        if args.command == "run":
            return run(Path(args.out), Path(args.plan), images_per_pair=args.images_per_pair,
                       deadline=deadline_of(args.deadline), cfg=cfg, retry_failed=args.retry_failed,
                       image_backend=image_backend, mesh_backend=mesh_backend, shard=parse_shard(args.shard))
        plan = read_plan(Path(args.plan))
        doc = build_survey(Path(args.out), plan, cfg, args.images_per_pair, Path(args.plan))
        log_print(f"generate survey: {len(doc['candidates'])} candidates -> {Path(args.out) / SURVEY_NAME}")
        return EXIT_OK
    except UsageError as exc:
        log_print(f"generate: {exc}")
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
