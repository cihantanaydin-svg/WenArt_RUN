"""The furniture library for the prep pod: the Objaverse survey and the shared steps of every source (thumbnails,
judging, acceptance, catalogue, report).

What (docs/milestone7.md §7, user decision 7): a larger furniture library than the 31 CC0 Poly Haven models, taken
from Objaverse 1.0 (Hugging Face ``allenai/objaverse`` @ 21e4e14, ODC-By 1.0). Nothing here runs in the session: the
prep pod runs the steps in this order and the integrator commits the catalogue into ``wenart/furniture/`` before the
full runs.

Milestone 8 (docs/milestone8.md §1, §2; user decisions 3 and 4 of 4 Oct 2026):

- One library pipeline for every source. The survey is per source: ``survey`` here (Objaverse, ``survey.json``),
  ``python -m wenart.assets.abo survey`` (``survey_abo.json``) and ``python -m wenart.assets.generate run``
  (``survey_generated.json``); every later step reads the candidates of every survey file present in ``--out``
  (``load_candidates``; field ``source``). Records keep the M7 shape plus ``source``, ``licence_flag``,
  ``style_hint``, ``kind`` (``furniture`` / ``decor``), ``decor_type``, ``units_known`` and ``extents_raw``.
- Objaverse: the licence filter is gone (any licence; ``licence_flag`` null for CC0 / CC BY 4.0, else
  ``non_commercial`` / ``share_alike`` / ``no_derivatives`` / ``unknown``; the credit fields are still required),
  <= 24 candidates per type.
- Thumbnails: a record with ``units_known`` (ABO: metres) skips the unit guess and is refused when its measured box is
  outside the type's range (no normalisation); a documented front (ABO: glTF +Z = -Y) replaces the geometric front
  (the geometric check is kept in the note); every bed gets ``deck_height_m`` (the median of 5 downward rays inside
  the inner 50 % of the footprint, Z-up model frame, metres; ``deck_height``).
- Decor (``kind: decor``; ``decor_type`` cushion, plant, rug, wall_art): thumbnails, a judge question of its own
  (``is_decor_type``: a rug is a rug, a planter holds a plant) and acceptance (<= 16 per decor type).
- Accept: beds both judges see without a mattress are bed frames (``bed_frame: true``) when the deck was measured,
  else refused ``no_deck``; <= 12 per furniture type, <= 3 per (type, style family), ranked by mean quality, then
  source order (abo, polyhaven, objaverse, generated); ``--sources`` limits a run to some sources (the prep job's
  first accept over the real models before the generation).
- ``write-catalog`` writes ``catalog_library.json`` (``wenart.furniture.catalog.load`` merges it; the M7
  ``catalog_objaverse.json`` is only a fallback there) with the GLBs in ``<assets>/models/<source>/<uid>.glb``; the
  report and ``ATTRIBUTION.md`` list every source, credit line and licence flag.

The steps as Milestone 7 built them (the Milestone 8 changes above apply on top of this text):

1. ``survey``: downloads ``lvis-annotations.json.gz``, ``object-paths.json.gz`` and the metadata shards into the
   container-disk Hugging Face cache (``--cache /opt/wenart/hf``), maps LVIS categories to furniture types
   (``objaverse.yaml``), keeps CC0 / CC BY 4.0 objects with a full credit (title, author, link), face count
   2k-150k and a GLB <= 40 MB, ranks by likes then views and downloads <= 8 candidates per type that are textured
   or vertex-coloured -> ``survey.json``.
2. ``thumbnails``: one Blender process (Cycles, GPU when available, 16 spp, 256 px) imports every candidate GLB
   like the scene builder does (``wenart.blender.furniture.import_gltf_geometry``), measures it in the Z-up Blender
   frame and renders four views framed on its box, one from each side (camera on the -Y, +X, +Y, -X side, 30
   degrees above), so a judge's ``front_view`` names one model axis; then, outside Blender, the unit guess (x1,
   0.01, 0.0254, 0.001: the one factor that puts the box in the type's size range and height range; several ->
   refused; none -> the units are unknown and the box is normalised by type, scaled to the type's typical
   footprint, refused only when its proportions are outside the type's ranges), the bed split (single / double
   by width, by the proportions when normalised, then <= 8 per type), the geometric front (the
   Poly Haven rule: taller side = back for seating and beds, door/drawer side = front for cabinets, panel side =
   back for open shelves) and the 2 x 2 judging sheet -> ``thumbnails.json``, ``judge/sheets/<uid>.jpg`` (512 px),
   ``thumbs/<type>/<uid>.jpg`` (256 px) and ``thumbs/NOTICE.md``. ``--work`` holds the views and measurements
   (put it outside the results folder: ``/workspace/library-work`` on the pod, so a resumed pod reuses them).
3. ``judge-requests``: one request per sheet (``judge/requests.json``, the recognition request shape of
   ``wenart.recognition.answers`` with task ``library_judge`` and a per-item prompt that names the type).
4. ``judge --model-key qwen|glm``: run inside the prep pod's Qwen and GLM sessions; temperature 0, seed 0,
   structured output, schema-validated; answers in ``judge/answers_<slug>.json`` (the recognition ``AnswerStore``
   format, reused while key and ``input_sha256`` match). ``judge-status`` counts them.
5. ``accept``: §7.2 rules: both passes ``is_single_object`` and ``matches_type``, both ``photoreal_quality`` >= 4,
   beds both ``has_mattress``, the box in the type's range, for every type with a front both passes give the
   same ``front_view`` and it equals the geometric front ("front not agreed" otherwise), ``styles`` = the
   intersection of both answers (``neutral`` only when both list it; empty -> refused); <= 6 per type ->
   ``accepted.json``.
6. ``write-catalog``: ``catalog_objaverse.json`` entries with the frame fields of ``wenart.furniture.catalog``
   (metres, Z-up model frame of the importer), the §6.6 fields, the §7.3 attribution line and the ODC-By notice;
   the accepted GLBs are copied to ``<assets>/models/objaverse/<uid>.glb`` (``--assets /workspace/assets``) and
   their sha256 recorded (``wenart.assets.models.fetch_objaverse_cached`` checks it on every full run). The boxes
   are metres: the raw GLB box times ``unit_scale``, which the scene builder applies to the imported mesh.
7. ``report``: ``library_report.md`` (counts, refusals by reason, licence values seen, style coverage per type and
   family, the attribution list, the ODC-By notice).

Why so many checks: the per-object licences are uploader-declared (unverified: flag for commercial use), the
metadata says nothing about scale or orientation, and the furniture rules need a model that is one piece, of the
drawn type, with a known front. Every refusal keeps its reason; nothing is guessed silently (CLAUDE.md).

CLI (all steps read and write ``--out``, the prep job's library folder)::

    python -m wenart.assets.objaverse survey --out DIR [--cache /opt/wenart/hf | --mirror DIR] [--no-download]
    python -m wenart.assets.objaverse thumbnails --out DIR [--work DIR] [--blender PATH] [--device auto|cpu]
        [--deadline T]
    python -m wenart.assets.objaverse judge-requests --out DIR
    python -m wenart.assets.objaverse judge --out DIR --model-key qwen|glm [--server URL] [--workers N]
        [--deadline T] [--seed-answers DIR]
    python -m wenart.assets.objaverse judge-status --out DIR
    python -m wenart.assets.objaverse accept --out DIR [--sources abo,objaverse]
    python -m wenart.assets.objaverse write-catalog --out DIR [--assets /workspace/assets]
    python -m wenart.assets.objaverse report --out DIR

Exit codes: 0 done, 1 the step ran but produced nothing usable (no candidate, nothing accepted, Blender failed),
2 usage or server error, 3 cut by the deadline (``--deadline`` or ``WENART_DEADLINE``, epoch seconds).

Verified from the session (3 Oct 2026, Hugging Face API, no LFS download): the file names, the 160 metadata shards
``metadata/000-000.json.gz`` ... ``000-159.json.gz`` and the 160 ``glbs/000-NNN`` folders, the dataset licence
(ODC-By 1.0) and the README's per-object licence list. Not verified (LFS is blocked here): the licence strings and
metadata field names inside the shards and the LVIS category names; they live in ``objaverse.yaml`` marked "to
verify on the pod", the survey records what it meets (licence values, metadata keys, missing categories) and
``tests/gpu/test_library.py`` fails on a name that is not found. A wrong name can only refuse objects.

Inside Blender (``blender -b --python wenart/assets/objaverse.py -- blender-thumbs <jobs.json>``) this file runs
as a plain script: its top-level imports are the standard library only, and the Blender side uses only the pure
helpers below (``front_stats``, ``newell``, ``view_location``, ``camera_distance``, ``deck_height``, ``write_json``).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import queue
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional

HERE = Path(__file__).resolve().parent
CONFIG_PATH = HERE / "objaverse.yaml"
SIZE_TABLE_PATH = HERE.parent / "recognition" / "size_table.yaml"
FURNITURE_DIR = HERE.parent / "furniture"
SCHEMA_VERSION = "0.1"
SOURCE = "objaverse"
TASK = "library_judge"
JUDGE_VERSION = "m7.1"
MODEL_KEYS: tuple[str, ...] = ("qwen", "glm")         # pass 1, pass 2 (check.yaml models)
CC0, CC_BY = "CC0", "CC-BY-4.0"                       # wenart.furniture.catalog LICENCE / CC_BY
ID_PREFIX = "objaverse_"
CACHE_REL = "models/objaverse"                        # <assets>/models/objaverse/<uid>.glb (assets.models)
# The four judging views: the camera sits on this side of the model (model frame of the importer, Z up), so a
# judge's front_view 0..3 names the model axis its front points along.
VIEW_SIDES: tuple[str, ...] = ("-Y", "+X", "+Y", "-X")
VIEW_PLACES: tuple[str, ...] = ("top left", "top right", "bottom left", "bottom right")
FRONTLESS_RULE = "none"
EXIT_OK, EXIT_FAIL, EXIT_SERVER, EXIT_DEADLINE = 0, 1, 2, 3
DEFAULT_SERVER = "http://127.0.0.1:8001/v1"

SURVEY_NAME = "survey.json"
# Every source's survey file in the library folder (objaverse.yaml survey_files; docs/milestone8.md §2).
SURVEY_FILES: dict[str, str] = {"objaverse": SURVEY_NAME, "abo": "survey_abo.json",
                                "generated": "survey_generated.json"}
SOURCES: tuple[str, ...] = tuple(SURVEY_FILES)
REAL_SOURCES: tuple[str, ...] = ("abo", "objaverse")       # the generation plan follows their accepted models
SOURCE_ORDER: tuple[str, ...] = ("abo", "polyhaven", "objaverse", "generated")   # rank order of docs/milestone8.md §2
DECOR_TYPES: tuple[str, ...] = ("cushion", "plant", "rug", "wall_art",             # = catalog.DECOR_TYPES
                                 "vase", "bowl", "plant_small", "table_lamp", "mirror")   # Milestone 9 (§3)
BED_TYPES: tuple[str, ...] = ("bed_single", "bed_double")
DOCUMENTED_RULE = "documented"                        # a front only the source's documented convention decides
THUMBS_JSON = "thumbnails.json"
ACCEPTED_NAME = "accepted.json"
CATALOG_NAME = "catalog_library.json"                 # Milestone 8 (replaces catalog_objaverse.json)
OLD_CATALOG_NAME = "catalog_objaverse.json"           # Milestone 7
REPORT_NAME = "library_report.md"
JUDGE_DIR = "judge"
REQUESTS_NAME = "requests.json"
SHEETS_DIR = "sheets"
THUMBS_DIR = "thumbs"
NOTICE_NAME = "NOTICE.md"
WORK_DIR = "work"

_UID_RE = re.compile(r"[A-Za-z0-9_-]{1,64}")          # as wenart.assets.models._UID_RE
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GLB_MAGIC, CHUNK_JSON = 0x46546C67, 0x4E4F534A          # b"glTF", b"JSON" (little endian)

# Readable text of the refusal codes (report, accepted.json).
REASONS: dict[str, str] = {
    "several_types": "in LVIS categories of different furniture types",
    "bad_uid": "uid is not a plain object id",
    "no_object_path": "no path in object-paths.json.gz",
    "bad_object_path": "object path not of the form glbs/<folder>/<uid>.glb",
    "no_metadata": "no metadata record",
    "no_credit": "credit field missing (title, author or link)",
    "face_count": "face count outside 2k-150k (fixture categories: 800-400k, docs/milestone9.md §2.2)",
    "glb_size": "GLB larger than the source's limit (Objaverse 40 MB, ABO 60 MB)",
    "download_failed": "download failed",
    "glb_unreadable": "GLB header unreadable",
    "untextured": "no image texture and no vertex colours",
    "not_rendered": "not rendered (Blender stopped before it)",
    "blender_error": "Blender could not import or render it",
    "unit_none": "no unit factor fits and the box proportions (footprint, height / width) are outside the type's "
                 "ranges",
    "unit_ambiguous": "more than one unit factor fits (never guessed)",
    "size_range": "box outside the resolved type's size range (units known: never normalised)",
    "not_judged": "an answer of a judge is missing",
    "not_single": "not a single object (a judge)",
    "type_mismatch": "not the furniture type (a judge)",
    "not_decor_type": "not the decor type (a judge; a planter must hold a plant)",
    "quality": "photoreal quality below 4 (a judge)",
    "no_mattress": "bed without a mattress (a judge)",
    "mattress_not_agreed": "the judges disagree whether the bed has a mattress",
    "no_deck": "bed frame without a measurable deck (5 downward rays)",
    "front_not_agreed": "front not agreed (judges and geometry or the documented front)",
    "no_common_style": "no style both judges name",
    "over_candidate_limit": "over the candidates of its source and type after the bed split",
    "over_type_limit": "over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1)",
    "over_style_limit": "every style family it fits already has its share of models of its type (no fill pass)",
    "glb_changed": "GLB sha256 differs from the survey (and no copy in the assets cache)",
}


# --------------------------------------------------------------------------
# Small helpers (stdlib only: also used inside Blender)
# --------------------------------------------------------------------------

def write_json(path: Path, data) -> Path:
    """indent=1, ensure_ascii=False, via a temporary file (as every M5/M7 JSON)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def read_json(path: Path) -> Optional[dict]:
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def read_json_gz(path: Path):
    with gzip.open(Path(path), "rb") as fh:
        return json.loads(fh.read().decode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(description) -> str:
    """sha256 of sorted-key compact JSON (the recognition ``input_sha256`` convention)."""
    text = json.dumps(description, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def now_utc() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def deadline_of(value: Optional[float]) -> Optional[float]:
    """``--deadline`` or the ``WENART_DEADLINE`` env (epoch seconds), None when neither is set."""
    if value is not None:
        return float(value)
    env = os.environ.get("WENART_DEADLINE", "").strip()
    return float(env) if env else None


def reason_text(code: str, detail: str = "") -> str:
    text = REASONS.get(code, code)
    return f"{text}: {detail}" if detail else text


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def load_config(path: Optional[Path] = None) -> dict:
    """``objaverse.yaml`` as a dict."""
    import yaml
    return yaml.safe_load(Path(CONFIG_PATH if path is None else path).read_text(encoding="utf-8")) or {}


def config_sha256(cfg: dict) -> str:
    return canonical_sha256(cfg)


def load_size_table(path: Optional[Path] = None) -> tuple[dict, float]:
    """``wenart/recognition/size_table.yaml`` (read only) as ``({type: ((w0, w1), (d0, d1))}, tolerance)``."""
    import yaml
    data = yaml.safe_load(Path(SIZE_TABLE_PATH if path is None else path).read_text(encoding="utf-8")) or {}
    table = {}
    for name, spec in (data.get("types") or {}).items():
        w, d = spec["width"], spec["depth"]
        table[name] = ((float(w[0]), float(w[1])), (float(d[0]), float(d[1])))
    return table, float(data.get("tolerance", 0.15))


def library_size_table(cfg: dict, path: Optional[Path] = None) -> tuple[dict, float]:
    """``load_size_table`` plus the decor footprints of ``objaverse.yaml`` ``decor_sizes`` (docs/milestone8.md §4)."""
    table, tol = load_size_table(path)
    for name, spec in (cfg.get("decor_sizes") or {}).items():
        w, d = spec["width"], spec["depth"]
        table[name] = ((float(w[0]), float(w[1])), (float(d[0]), float(d[1])))
    return table, tol


def heights_of(cfg: dict) -> dict:
    return {t: spec["height"] for t, spec in cfg["types"].items()}


_LVIS_STOP = {"of", "the", "and", "a", "for", "furniture"}


def lvis_near_names(category: str, lvis: dict, limit: int = 20) -> list[str]:
    """LVIS category names of the annotation file that share a word stem (first 5 letters of a word of >= 4) with a
    missing ``category``: evidence for choosing an alternate name on the next survey, never a mapping by itself."""
    words = {w[:5] for w in re.split(r"[^a-z]+", category.casefold()) if len(w) >= 4 and w not in _LVIS_STOP}
    out = []
    for name in sorted(lvis):
        tokens = {w[:5] for w in re.split(r"[^a-z]+", str(name).casefold()) if len(w) >= 4 and w not in _LVIS_STOP}
        if name != category and words & tokens:
            out.append(name)
    return out[:limit]


def group_key(types) -> str:
    """The candidate group of a category: its type, or ``bed_double|bed_single`` for a category that maps to two."""
    return "|".join(types)


def style_values() -> tuple[str, ...]:
    from wenart.furniture import catalog as C
    return C.style_values()


# --------------------------------------------------------------------------
# Dataset access: the Hugging Face cache on the pod, or a local mirror (tests)
# --------------------------------------------------------------------------

class LocalHub:
    """A folder laid out like the dataset repository (tests, or files fetched earlier)."""

    def __init__(self, root: Path):
        self.root = Path(root)

    def path(self, filename: str) -> Path:
        p = self.root / filename
        if not p.is_file():
            raise FileNotFoundError(f"{filename} is not in {self.root}")
        return p

    def describe(self) -> str:
        return f"local mirror {self.root}"


class HFHub:
    """``huggingface_hub.hf_hub_download`` of the pinned dataset revision into ``<cache>/hub`` (HF_HOME layout).

    The prep pod passes ``--cache /opt/wenart/hf`` (container disk, CLAUDE.md); offline (``HF_HUB_OFFLINE``) only
    cached files are read. huggingface_hub is imported lazily (the session has none)."""

    def __init__(self, repo: str, revision: str, cache: Optional[Path] = None, repo_type: str = "dataset"):
        self.repo, self.revision, self.cache, self.repo_type = repo, revision, cache, repo_type

    def path(self, filename: str) -> Path:
        from huggingface_hub import hf_hub_download

        from wenart import hfcache
        kwargs = {"repo_id": self.repo, "filename": filename, "repo_type": self.repo_type,
                  "revision": self.revision}
        if self.cache:
            kwargs["cache_dir"] = str(Path(self.cache) / "hub")
        if hfcache.hub_offline():
            kwargs["local_files_only"] = True
        return Path(hf_hub_download(**kwargs))

    def describe(self) -> str:
        where = f"{Path(self.cache) / 'hub'}" if self.cache else "the default HF cache"
        return f"huggingface.co/datasets/{self.repo}@{self.revision} -> {where}"


# --------------------------------------------------------------------------
# Metadata: licence, credit, prefilter numbers
# --------------------------------------------------------------------------

def dig(record, path):
    """``record[k1][k2]...`` for a key or a key list; None when a step is missing."""
    keys = path if isinstance(path, list) else [path]
    cur = record
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def _text(value) -> Optional[str]:
    if not isinstance(value, str):
        return None
    value = " ".join(value.split())
    return value or None


def _int(value) -> Optional[int]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(value)


def licence_value(raw) -> Optional[str]:
    """The metadata licence as a compare string: casefolded, spaces collapsed. A dict (Sketchfab API form) gives
    its ``slug`` (else ``label``)."""
    if isinstance(raw, dict):
        raw = raw.get("slug") or raw.get("label")
    if not isinstance(raw, str):
        return None
    return " ".join(raw.strip().casefold().split()) or None


LICENCE_FLAG_NAMES = ("non_commercial", "share_alike", "no_derivatives", "unknown")   # = catalog.FLAGS
UNKNOWN_LICENCE = "unknown"


def classify_licence(raw, cfg: dict) -> tuple[str, Optional[str], str]:
    """``(catalogue licence, licence_flag, detail)`` of a metadata licence value (docs/milestone8.md §2: every
    licence is taken; M7 refused all but CC0 / CC BY 4.0). ``accept`` spellings give CC0 / CC BY 4.0 with flag None;
    ``flagged`` spellings their licence with its flag (``wenart.furniture.catalog.LICENCE_FLAGS``); any other value,
    or none, the licence ``unknown`` with flag ``unknown`` (the detail says what was there)."""
    from wenart.furniture import catalog as C
    value = licence_value(raw)
    lic = cfg["licences"]
    unknown = str(lic.get("unknown") or UNKNOWN_LICENCE)
    if value is None:
        return unknown, C.licence_flag_of(unknown), "no licence in the metadata"
    for table in (lic["accept"], lic.get("flagged") or {}):
        for name, spellings in table.items():
            if value in {" ".join(str(s).casefold().split()) for s in spellings}:
                return name, C.licence_flag_of(name), "" if table is lic["accept"] else value
    return unknown, C.licence_flag_of(unknown), f"licence value {value!r} not known"


def credit_of(meta: dict, fields: dict) -> tuple[dict, list[str]]:
    """``({"title", "author", "source_url"}, missing field names)`` from a metadata record."""
    title = _text(dig(meta, fields["title"]))
    author = _text(dig(meta, fields["author"])) or _text(dig(meta, fields.get("author_fallback", [])))
    url = _text(dig(meta, fields["source_url"]))
    if url is not None and not url.startswith(("https://", "http://")):
        url = None
    credit = {"title": title, "author": author, "source_url": url}
    return credit, [k for k, v in credit.items() if v is None]


def face_count_of(meta: dict, fields: dict) -> Optional[int]:
    value = _int(dig(meta, fields["face_count"]))
    return value if value is not None else _int(dig(meta, fields.get("face_count_fallback", [])))


def prefer_hit(meta: dict, fields: dict, words) -> bool:
    """True when the title or a tag name holds one of ``words`` (a ranking hint, never an acceptance rule)."""
    if not words:
        return False
    texts = [_text(dig(meta, fields["title"])) or ""]
    for tag in meta.get("tags") or []:
        if isinstance(tag, dict):
            texts.append(str(tag.get("name") or ""))
        elif isinstance(tag, str):
            texts.append(tag)
    blob = " ".join(texts).casefold()
    return any(re.search(rf"\b{re.escape(str(w).casefold())}", blob) for w in words)


def shard_of(object_path: str, uid: str, metadata_dir: str = "metadata") -> Optional[str]:
    """``metadata/000-023.json.gz`` for ``glbs/000-023/<uid>.glb``; None when the path has another form."""
    parts = str(object_path).split("/")
    if len(parts) != 3 or parts[0] != "glbs" or parts[2] != f"{uid}.glb" or not re.fullmatch(r"\d{3}-\d{3}", parts[1]):
        return None
    return f"{metadata_dir}/{parts[1]}.json.gz"


# --------------------------------------------------------------------------
# GLB container (pure: the JSON chunk only)
# --------------------------------------------------------------------------

def glb_json(path: Path) -> dict:
    """The JSON chunk of a binary glTF (``ValueError`` when the file is not GLB 2.0)."""
    with Path(path).open("rb") as fh:
        head = fh.read(12)
        if len(head) < 12:
            raise ValueError("file shorter than a GLB header")
        magic, version, _length = struct.unpack("<III", head)
        if magic != GLB_MAGIC:
            raise ValueError("not a GLB file (magic)")
        if version != 2:
            raise ValueError(f"GLB version {version}, expected 2")
        chunk = fh.read(8)
        if len(chunk) < 8:
            raise ValueError("GLB without a JSON chunk")
        clen, ctype = struct.unpack("<II", chunk)
        if ctype != CHUNK_JSON:
            raise ValueError("first GLB chunk is not JSON")
        data = fh.read(clen)
    return json.loads(data.decode("utf-8"))


def _uses_texture(value) -> bool:
    """True when a material dict references a texture (``{"...Texture": {"index": n}}`` at any depth)."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key.endswith("Texture") and isinstance(item, dict) and "index" in item:
                return True
            if _uses_texture(item):
                return True
    elif isinstance(value, list):
        return any(_uses_texture(v) for v in value)
    return False


def glb_info(path: Path) -> dict:
    """Counts from the GLB JSON: images, textures, materials, meshes, primitives, ``textured`` (an image used by a
    material), ``vertex_colours`` (a primitive with ``COLOR_0``), the extensions used."""
    doc = glb_json(path)
    meshes = doc.get("meshes") or []
    prims = [p for m in meshes for p in (m.get("primitives") or [])]
    materials = doc.get("materials") or []
    images = len(doc.get("images") or [])
    textures = len(doc.get("textures") or [])
    return {
        "images": images, "textures": textures, "materials": len(materials), "meshes": len(meshes),
        "primitives": len(prims),
        "textured": bool(images and textures and any(_uses_texture(m) for m in materials)),
        "vertex_colours": any("COLOR_0" in (p.get("attributes") or {}) for p in prims),
        "extensions_used": sorted(doc.get("extensionsUsed") or []),
        "extensions_required": sorted(doc.get("extensionsRequired") or []),
    }


# --------------------------------------------------------------------------
# 1. Survey
# --------------------------------------------------------------------------

def _refusal(uid: str, code: str, detail: str = "", **extra) -> dict:
    out = {"uid": uid, "code": code, "detail": detail}
    out.update({k: v for k, v in extra.items() if v is not None})
    return out


def _load_shards(hub, shards: list[str], wanted: dict[str, set], workers: int, log: Callable) -> dict:
    """``{uid: record}`` for the wanted uids of every shard (downloads in parallel, reads one at a time)."""
    from concurrent.futures import ThreadPoolExecutor

    records: dict[str, dict] = {}
    if not shards:
        return records
    with ThreadPoolExecutor(max_workers=max(1, int(workers))) as pool:
        futures = {name: pool.submit(hub.path, name) for name in shards}
        for n, name in enumerate(shards, 1):
            try:
                path = futures[name].result()
            except Exception as exc:  # noqa: BLE001 - the shard's objects are refused with the reason
                log(f"objaverse survey: {name} not available: {exc}")
                continue
            data = read_json_gz(path)
            for uid in wanted[name]:
                rec = data.get(uid) if isinstance(data, dict) else None
                if isinstance(rec, dict):
                    records[uid] = rec
            if n % 20 == 0:
                log(f"objaverse survey: {n}/{len(shards)} metadata shards read")
    return records


def survey(hub, out: Path, cfg: Optional[dict] = None, download: bool = True, workers: int = 8,
           log: Callable = print) -> dict:
    """§7.1: LVIS categories -> types, licence (any, flagged: docs/milestone8.md §2), credit, prefilter, rank,
    <= ``per_type_limit`` (24) candidates per type -> ``survey.json``.

    ``hub.path(filename)`` returns a local file of the dataset (``HFHub`` on the pod, ``LocalHub`` in tests).
    With ``download`` the candidates' GLBs are fetched in rank order (at most ``max_downloads_per_type`` per type)
    until ``per_type_limit`` pass the file checks (size, textured or vertex-coloured); without it the top of the
    ranking is listed without files.
    """
    cfg = cfg or load_config()
    out = Path(out)
    ds, fields, pre = cfg["dataset"], cfg["metadata_fields"], cfg["prefilter"]
    categories = cfg["categories"]
    lvis = read_json_gz(hub.path(ds["lvis_file"]))
    paths = read_json_gz(hub.path(ds["paths_file"]))
    if not isinstance(lvis, dict) or not isinstance(paths, dict):
        raise ValueError("lvis-annotations / object-paths are not JSON objects (format changed?)")
    found = {c: len(lvis.get(c) or []) for c in categories if c in lvis}
    missing_cats = sorted(c for c in categories if c not in lvis)
    near = {c: lvis_near_names(c, lvis) for c in missing_cats}
    for c in missing_cats:
        log(f"objaverse survey: LVIS category {c!r} not in {ds['lvis_file']}: its types stay parametric (a "
            f"warning, not a failure); names in the file that share a word: {near[c] or 'none'}")

    uid_cats: dict[str, list[str]] = {}
    for cat in categories:
        for uid in lvis.get(cat) or []:
            if cat not in uid_cats.setdefault(str(uid), []):
                uid_cats[str(uid)].append(cat)

    refused: list[dict] = []
    counts: dict[str, dict] = {}
    pools: dict[str, list[dict]] = {}
    wanted: dict[str, set] = {}
    staged: list[tuple[str, str, list[str], list[str]]] = []
    for uid in sorted(uid_cats):
        cats = uid_cats[uid]
        type_sets = {tuple(categories[c]["types"]) for c in cats}
        if len(type_sets) > 1:
            refused.append(_refusal(uid, "several_types", ", ".join(cats), categories=cats))
            continue
        types = list(next(iter(type_sets)))
        group = group_key(types)
        c = counts.setdefault(group, {"lvis": 0, "metadata": 0, "licence_ok": 0, "flagged": 0, "prefilter_ok": 0,
                                      "tried": 0, "candidates": 0, "not_selected": 0})
        c["lvis"] += 1
        if not _UID_RE.fullmatch(uid):
            refused.append(_refusal(uid, "bad_uid", "", categories=cats, group=group))
            continue
        opath = paths.get(uid)
        if not isinstance(opath, str):
            refused.append(_refusal(uid, "no_object_path", "", categories=cats, group=group))
            continue
        shard = shard_of(opath, uid, ds.get("metadata_dir", "metadata"))
        if shard is None:
            refused.append(_refusal(uid, "bad_object_path", opath, categories=cats, group=group))
            continue
        wanted.setdefault(shard, set()).add(uid)
        staged.append((uid, opath, cats, types))

    shards = sorted(wanted)
    log(f"objaverse survey: {len(uid_cats)} LVIS objects in {len(found)} categories; reading {len(shards)} shards")
    records = _load_shards(hub, shards, wanted, workers, log)

    licence_values: dict[str, int] = {}
    metadata_keys: set[str] = set()
    missing_fields: dict[str, int] = {}
    max_bytes = float(pre["max_glb_mb"]) * 1024 * 1024
    for uid, opath, cats, types in staged:
        group = group_key(types)
        c = counts[group]
        face_lo, face_hi = (int(v) for v in category_prefilter(pre, cats)["face_count"])
        meta = records.get(uid)
        if meta is None:
            refused.append(_refusal(uid, "no_metadata", "", categories=cats, group=group))
            continue
        c["metadata"] += 1
        metadata_keys.update(meta.keys())
        raw = dig(meta, fields["licence"])
        shown = licence_value(raw) or "(none)"
        licence_values[shown] = licence_values.get(shown, 0) + 1
        licence, flag, _detail = classify_licence(raw, cfg)    # every licence is taken (M8), flagged
        c["licence_ok" if flag is None else "flagged"] = c.get("licence_ok" if flag is None else "flagged", 0) + 1
        credit, missing = credit_of(meta, fields)
        for name in ("likes", "views"):
            if _int(dig(meta, fields[name])) is None:
                missing_fields[name] = missing_fields.get(name, 0) + 1
        if missing:
            for name in missing:
                missing_fields[name] = missing_fields.get(name, 0) + 1
            refused.append(_refusal(uid, "no_credit", ", ".join(missing), categories=cats, group=group))
            continue
        faces = face_count_of(meta, fields)
        if faces is None:
            missing_fields["face_count"] = missing_fields.get("face_count", 0) + 1
            refused.append(_refusal(uid, "face_count", "no face count in the metadata", categories=cats,
                                    group=group))
            continue
        if not face_lo <= faces <= face_hi:
            refused.append(_refusal(uid, "face_count", str(faces), categories=cats, group=group))
            continue
        size = _int(dig(meta, fields["glb_size"]))
        if size is not None and size > max_bytes:
            refused.append(_refusal(uid, "glb_size", f"{size / 1048576:.1f} MB (metadata)", categories=cats,
                                    group=group))
            continue
        c["prefilter_ok"] += 1
        words = []
        for cat in cats:
            words += list(categories[cat].get("prefer_words") or [])
        pools.setdefault(group, []).append({
            "uid": uid, "group": group, "types": types, "categories": cats, **credit,
            "licence": licence, "licence_raw": shown, "face_count": faces, "glb_size_meta": size,
            "texture_count": _int(dig(meta, fields["texture_count"])),
            "likes": _int(dig(meta, fields["likes"])) or 0, "views": _int(dig(meta, fields["views"])) or 0,
            "prefer_hit": prefer_hit(meta, fields, words), "object_path": opath,
            # Milestone 8 record fields (docs/milestone8.md §2)
            "source": SOURCE, "licence_flag": flag, "licence_url": licence_url(licence, cfg),
            "via": cfg["attribution"]["via"],
            "attribution": attribution_line(credit["title"], credit["author"], credit["source_url"], licence, cfg),
            "style_hint": None, "kind": "furniture", "decor_type": None, "units_known": False,
            "extents_raw": None,
        })
        if category_prefilter(pre, cats).get("allow_flat_colours"):
            pools[group][-1]["allow_flat_colours"] = True        # Milestone 9 fixtures (§2.2)

    candidates: list[dict] = []
    previous = previous_candidates(out)
    if previous:
        log(f"objaverse survey: {len(previous)} candidates of the earlier {SURVEY_NAME} come first in their types")
    for group in sorted(pools):
        pool = sorted(pools[group], key=lambda r: (not r["prefer_hit"], -r["likes"], -r["views"], r["uid"]))
        limits = group_prefilter(pre, [cat for rec in pool for cat in rec["categories"]])
        per_type = int(limits["per_type_limit"])
        max_dl = int(limits.get("max_downloads_per_type", 2 * per_type))
        cap = per_type * len(pool[0]["types"])
        dl_cap = max_dl * len(pool[0]["types"])
        c = counts[group]
        chosen = 0
        for rank, rec in enumerate(pool, 1):
            rec["rank"] = rank
        # Milestone 9: the candidates of the survey before this one come first (a wider prefilter must never push out
        # a model that was judged and accepted), then the rest in rank order.
        kept = [r for r in pool if r["uid"] in previous]
        for rec in kept + [r for r in pool if r["uid"] not in previous]:
            if chosen >= cap or (download and c["tried"] >= dl_cap):
                c["not_selected"] += 1
                continue
            if download:
                c["tried"] += 1
                problem = _fetch_candidate(hub, rec, max_bytes)
                if problem is not None:
                    refused.append(_refusal(rec["uid"], problem[0], problem[1], categories=rec["categories"],
                                            group=group))
                    continue
            chosen += 1
            c["candidates"] += 1
            candidates.append(rec)
        log(f"objaverse survey: {group}: {c['lvis']} LVIS objects, {c['licence_ok']} CC0/CC BY, "
            f"{c.get('flagged', 0)} flagged licences, {c['prefilter_ok']} past the prefilter, "
            f"{c['candidates']} candidates")

    refused_counts: dict[str, int] = {}
    for r in refused:
        refused_counts[r["code"]] = refused_counts.get(r["code"], 0) + 1
    doc = {
        "schema_version": SCHEMA_VERSION, "kind": "objaverse_survey", "source": SOURCE, "generated_utc": now_utc(),
        "dataset": {k: ds[k] for k in ("repo", "revision", "licence", "licence_url", "page") if k in ds},
        "hub": hub.describe() if hasattr(hub, "describe") else str(hub), "downloaded": bool(download),
        "config_sha256": config_sha256(cfg), "licences_verified": bool(cfg["licences"].get("verified")),
        "lvis": {"found": found, "missing": missing_cats, "categories_in_file": len(lvis), "near_missing": near},
        "licence_values": dict(sorted(licence_values.items(), key=lambda kv: (-kv[1], kv[0]))),
        "metadata_keys": sorted(metadata_keys), "missing_fields": dict(sorted(missing_fields.items())),
        "counts": counts, "refused_counts": dict(sorted(refused_counts.items())),
        "candidates": candidates, "refused": refused,
    }
    write_json(out / SURVEY_NAME, doc)
    return doc


def _fetch_candidate(hub, rec: dict, max_bytes: float) -> Optional[tuple[str, str]]:
    """Download one GLB and run the file checks; fills ``glb``, ``glb_sha256``, ``glb_bytes``, ``glb_info`` or
    returns ``(code, detail)``."""
    try:
        local = Path(hub.path(rec["object_path"]))
    except Exception as exc:  # noqa: BLE001 - recorded as a refusal
        return "download_failed", f"{type(exc).__name__}: {exc}"
    size = local.stat().st_size
    if size > max_bytes:
        return "glb_size", f"{size / 1048576:.1f} MB (file)"
    try:
        info = glb_info(local)
    except (ValueError, OSError, UnicodeDecodeError) as exc:
        return "glb_unreadable", str(exc)
    if not (info["textured"] or info["vertex_colours"]):
        if not (rec.get("allow_flat_colours") and info["materials"] > 0):
            return "untextured", f"{info['images']} images, {info['textures']} textures, no COLOR_0"
        info = dict(info, flat_colours=True)        # a fixture with material colours only (docs/milestone9.md §2.2)
    rec.update({"glb": str(local), "glb_sha256": sha256_file(local), "glb_bytes": size, "glb_info": info})
    return None


def previous_candidates(out: Path) -> set:
    """The uids of the candidates of an earlier ``survey.json`` in ``out`` (empty without one)."""
    doc = read_json(Path(out) / SURVEY_NAME) if (Path(out) / SURVEY_NAME).is_file() else None
    return {str(c["uid"]) for c in (doc or {}).get("candidates") or [] if isinstance(c, dict) and c.get("uid")}


def category_prefilter(pre: dict, categories) -> dict:
    """The prefilter of an object of ``categories``: ``objaverse.yaml prefilter`` with the ``overrides`` of the first
    of its categories that has one (Milestone 9 fixtures: ``face_count``, ``allow_flat_colours``,
    ``per_type_limit``, ``max_downloads_per_type``); without one the M8 values."""
    base = {k: v for k, v in pre.items() if k != "overrides"}
    overrides = pre.get("overrides") or {}
    for cat in categories or ():
        if isinstance(overrides.get(cat), dict):
            return dict(base, **overrides[cat])
    return base


def group_prefilter(pre: dict, categories) -> dict:
    """The candidate limits of a group: the largest ``per_type_limit`` / ``max_downloads_per_type`` of the categories
    of its objects (their ``category_prefilter``); the M8 values when none has an override."""
    out = {k: v for k, v in pre.items() if k != "overrides"}
    for cat in sorted(set(categories or ())):
        own = category_prefilter(pre, [cat])
        for key in ("per_type_limit", "max_downloads_per_type"):
            if key in own and int(own[key]) > int(out.get(key, 0)):
                out[key] = int(own[key])
    return out


# --------------------------------------------------------------------------
# Every source's survey records (docs/milestone8.md §2)
# --------------------------------------------------------------------------

def licence_url(licence: str, cfg: dict) -> str:
    """The licence's URL (objaverse.yaml licences.urls; a generated model has none: the empty string)."""
    urls = (cfg.get("licences") or {}).get("urls") or {}
    return str(urls.get(licence) or "")


def normalise_record(rec: dict, source: str) -> dict:
    """A survey record of ``source`` with the Milestone 8 fields filled where an older (M7) or a minimal record
    leaves them out: ``source``, ``types`` / ``group``, ``kind`` (furniture), ``decor_type``, ``units_known`` (False),
    ``style_hint``, ``extents_raw``, ``licence_flag`` (from the licence). ``UsageError`` when the record names
    another source or has no uid."""
    from wenart.furniture import catalog as C
    out = dict(rec)
    if not out.get("uid"):
        raise UsageError(f"{SURVEY_FILES[source]}: a candidate without uid")
    if out.setdefault("source", source) != source:
        raise UsageError(f"{SURVEY_FILES[source]}: candidate {out['uid']} has source {out['source']!r}, not {source}")
    if not out.get("types"):
        out["types"] = [out["type"]] if out.get("type") else []
    out.setdefault("group", group_key(out["types"]))
    out.setdefault("kind", "decor" if out["types"] and out["types"][0] in DECOR_TYPES else "furniture")
    out.setdefault("decor_type", out["types"][0] if out["kind"] == "decor" and out["types"] else None)
    out.setdefault("units_known", False)
    out.setdefault("style_hint", None)
    out.setdefault("extents_raw", None)
    out.setdefault("categories", [])
    if "licence_flag" not in out:
        out["licence_flag"] = C.licence_flag_of(out.get("licence"))
    return out


def load_surveys(out: Path) -> dict:
    """``{source: survey document}`` of every survey file present in ``out`` (``SURVEY_FILES`` order)."""
    docs = {}
    for source, name in SURVEY_FILES.items():
        doc = read_json(Path(out) / name)
        if doc is not None:
            docs[source] = doc
    return docs


def load_candidates(out: Path, sources=None) -> list[dict]:
    """The candidates of every survey file in ``out`` (``normalise_record``d, in ``SURVEY_FILES`` order), or of
    ``sources`` only. ``UsageError`` when no survey file is there or a uid occurs twice."""
    docs = load_surveys(out)
    if not docs:
        raise UsageError(f"no survey file ({', '.join(SURVEY_FILES.values())}) in {out}: run a survey first")
    seen: dict[str, str] = {}
    cands = []
    for source, doc in docs.items():
        if sources is not None and source not in sources:
            continue
        for rec in doc.get("candidates") or []:
            rec = normalise_record(rec, source)
            if rec["uid"] in seen:
                raise UsageError(f"uid {rec['uid']} is a candidate of {seen[rec['uid']]} and {source}")
            seen[rec["uid"]] = source
            cands.append(rec)
    return cands


def credit_line(cand: dict, cfg: dict) -> str:
    """The credit line of a candidate: its survey's ``attribution`` (ABO, generated, M8 Objaverse), else the §7.3
    Objaverse line built from its credit fields (M7 records)."""
    if cand.get("attribution"):
        return str(cand["attribution"])
    if cand.get("source") == "generated":
        return (f'"{cand.get("title") or cand["uid"]}": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no '
                "third-party credit")
    return attribution_line(cand.get("title") or cand["uid"], cand.get("author") or "unknown author",
                            cand.get("source_url") or "", cand.get("licence") or UNKNOWN_LICENCE, cfg)


# --------------------------------------------------------------------------
# Geometry (pure; also run inside Blender)
# --------------------------------------------------------------------------

def bounds(points) -> tuple[list[float], list[float]]:
    mins = [min(p[i] for p in points) for i in range(3)]
    maxs = [max(p[i] for p in points) for i in range(3)]
    return mins, maxs


def newell(verts) -> tuple[tuple[float, float, float], float]:
    """Unit normal and area of a planar polygon (Newell's method; a degenerate polygon gives (0, 0, 0), 0)."""
    nx = ny = nz = 0.0
    n = len(verts)
    for i in range(n):
        x0, y0, z0 = verts[i]
        x1, y1, z1 = verts[(i + 1) % n]
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length <= 0.0:
        return (0.0, 0.0, 0.0), 0.0
    return (nx / length, ny / length, nz / length), 0.5 * length


def poly_record(verts) -> tuple:
    """``(cx, cy, cz, nx, ny, nz, area)`` of one polygon (world coordinates)."""
    (nx, ny, nz), area = newell(verts)
    k = float(len(verts))
    return (sum(v[0] for v in verts) / k, sum(v[1] for v in verts) / k, sum(v[2] for v in verts) / k,
            nx, ny, nz, area)


SIDES = ("-x", "+x", "-y", "+y")


def front_stats(points, polys=(), top_fraction: float = 0.3, side_fraction: float = 0.05,
                normal_dot: float = 0.9) -> dict:
    """The raw numbers of the geometric front check, unit-free.

    ``top_centroid_n``: mean x, y of the vertices in the top ``top_fraction`` of the height, minus the box centre,
    divided by the x / y extents (``measure_gltf``'s ``top_centroid_xy`` normalised); ``side_counts``: vertices
    within ``side_fraction`` of the extent of each side (``-x``, ``+x``, ``-y``, ``+y``, as ``measure_gltf``);
    ``panel_fraction``: area of the faces in that slab whose normal points out of that side (dot >=
    ``normal_dot``), divided by the box face of that side (a closed back panel gives about 1, an open side ~0).
    """
    mins, maxs = bounds(points)
    ext = [maxs[i] - mins[i] for i in range(3)]
    centre = [(mins[i] + maxs[i]) / 2.0 for i in range(3)]
    z_cut = mins[2] + (1.0 - top_fraction) * ext[2]
    top = [p for p in points if p[2] >= z_cut] or list(points)
    tc = [sum(p[0] for p in top) / len(top) - centre[0], sum(p[1] for p in top) / len(top) - centre[1]]
    top_n = [tc[0] / ext[0] if ext[0] > 0 else 0.0, tc[1] / ext[1] if ext[1] > 0 else 0.0]
    tol = [side_fraction * e for e in ext]
    counts = {
        "-x": sum(1 for p in points if p[0] <= mins[0] + tol[0]),
        "+x": sum(1 for p in points if p[0] >= maxs[0] - tol[0]),
        "-y": sum(1 for p in points if p[1] <= mins[1] + tol[1]),
        "+y": sum(1 for p in points if p[1] >= maxs[1] - tol[1]),
    }
    area = {s: 0.0 for s in SIDES}
    for cx, cy, _cz, nx, ny, _nz, a in polys:
        if cx <= mins[0] + tol[0] and nx <= -normal_dot:
            area["-x"] += a
        if cx >= maxs[0] - tol[0] and nx >= normal_dot:
            area["+x"] += a
        if cy <= mins[1] + tol[1] and ny <= -normal_dot:
            area["-y"] += a
        if cy >= maxs[1] - tol[1] and ny >= normal_dot:
            area["+y"] += a
    face_x, face_y = ext[1] * ext[2], ext[0] * ext[2]
    panel = {s: round(area[s] / (face_x if s.endswith("x") else face_y), 4)
             if (face_x if s.endswith("x") else face_y) > 0 else 0.0 for s in SIDES}
    return {"bbox_min": [float(v) for v in mins], "bbox_max": [float(v) for v in maxs],
            "extents": [float(v) for v in ext], "vertices": len(points), "polygons": len(polys),
            "top_centroid_n": [round(v, 4) for v in top_n], "side_counts": counts, "panel_fraction": panel}


def deck_points(mins, maxs, offset: float = 0.2) -> list[tuple[float, float]]:
    """The five ray positions of the deck measurement: the footprint centre and the points at +-``offset`` of the
    box's x and y extents from it (inside the inner 50 % of the footprint for an offset below 0.25)."""
    ex, ey = maxs[0] - mins[0], maxs[1] - mins[1]
    cx, cy = (mins[0] + maxs[0]) / 2.0, (mins[1] + maxs[1]) / 2.0
    return [(cx, cy)] + [(cx + sx * offset * ex, cy + sy * offset * ey) for sy in (-1, 1) for sx in (-1, 1)]


def _triangle_z(a, b, c, px: float, py: float) -> Optional[float]:
    """The z of triangle ``abc`` above the point (px, py) (None when the point is outside its XY projection or the
    triangle stands vertical)."""
    d = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
    span = (max(a[0], b[0], c[0]) - min(a[0], b[0], c[0])) + (max(a[1], b[1], c[1]) - min(a[1], b[1], c[1]))
    if abs(d) <= 1e-9 * span * span:
        return None
    l1 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / d
    l2 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / d
    l3 = 1.0 - l1 - l2
    eps = 1e-9
    if l1 < -eps or l2 < -eps or l3 < -eps:
        return None
    return l1 * a[2] + l2 * b[2] + l3 * c[2]


def deck_height(polygons, mins, maxs, offset: float = 0.2) -> dict:
    """The deck of a bed (docs/milestone8.md §2), in the model's own units, Z up: five rays straight down at
    ``deck_points``; each ray's hit is the topmost polygon surface above its point (polygons: lists of world
    vertices, fanned into triangles), measured from the box bottom. ``{"points", "hits_raw": [h | None] * 5, "hits",
    "height_raw": median of the hits | None}``; the unit scale and the plausibility checks are applied by the caller
    (``thumbnails``, ``decide``)."""
    pts = deck_points(mins, maxs, offset)
    best: list[Optional[float]] = [None] * len(pts)
    for poly in polygons:
        if len(poly) < 3:
            continue
        a = poly[0]
        for k in range(1, len(poly) - 1):
            b, c = poly[k], poly[k + 1]
            x0, x1 = min(a[0], b[0], c[0]), max(a[0], b[0], c[0])
            y0, y1 = min(a[1], b[1], c[1]), max(a[1], b[1], c[1])
            for i, (px, py) in enumerate(pts):
                if px < x0 or px > x1 or py < y0 or py > y1:
                    continue
                z = _triangle_z(a, b, c, px, py)
                if z is not None and (best[i] is None or z > best[i]):
                    best[i] = z
    hits = [None if z is None else round(float(z) - float(mins[2]), 6) for z in best]
    got = sorted(h for h in hits if h is not None)
    if not got:
        median = None
    elif len(got) % 2:
        median = got[len(got) // 2]
    else:
        median = (got[len(got) // 2 - 1] + got[len(got) // 2]) / 2.0
    return {"points": [[round(x, 6), round(y, 6)] for x, y in pts], "hits_raw": hits, "hits": len(got),
            "height_raw": median, "offset": offset}


def _axis_name(axis: str, sign: int) -> str:
    return ("-" if sign < 0 else "+") + axis.upper()


def geometric_front(stats: dict, rule: str, rules: dict) -> tuple[Optional[str], str]:
    """``(front axis | None, note)`` by the rule of the type (``objaverse.yaml`` types/front_rules).

    - ``back_taller`` (seating, beds, toilet, washbasin): the top vertices sit over the back;
    - ``detail_side`` (cabinets, appliances): the slab with more vertices (doors, drawers, handles) is the front;
    - ``open_side`` (open shelves): the side with a closed outward panel is the back;
    - ``none``: no front.
    None means the geometry does not decide (the object is then refused "front not agreed")."""
    if rule == FRONTLESS_RULE:
        return None, "type without a front"
    if rule == DOCUMENTED_RULE:
        return None, "documented: only the source's documented front decides (the geometry cannot tell)"
    if rule == "back_taller":
        p = rules["back_taller"]
        nx, ny = stats["top_centroid_n"]
        axis, v, other = ("x", nx, ny) if abs(nx) >= abs(ny) else ("y", ny, nx)
        if abs(v) < float(p["min_offset"]):
            return None, (f"back_taller: top centroid offset {v:+.3f} of the extent on {axis} is below "
                          f"{p['min_offset']}: no taller side")
        if abs(v) < float(p["dominance"]) * abs(other):
            return None, f"back_taller: offsets {nx:+.3f} (x) and {ny:+.3f} (y) do not single out one axis"
        back = 1 if v > 0 else -1
        front = _axis_name(axis, -back)
        return front, (f"back_taller: the top {round(float(rules.get('top_fraction', 0.3)) * 100)} % of the vertices "
                       f"sit toward {_axis_name(axis, back)} ({v:+.3f} of the extent): front {front}")
    if rule == "detail_side":
        p = rules["detail_side"]
        c = stats["side_counts"]

        def ratio(a, b):
            return max(a, b) / max(1, min(a, b))
        rx, ry = ratio(c["-x"], c["+x"]), ratio(c["-y"], c["+y"])
        axis, r, other = ("x", rx, ry) if rx >= ry else ("y", ry, rx)
        lo, hi = c[f"-{axis}"], c[f"+{axis}"]
        if max(lo, hi) < int(p["min_count"]):
            return None, f"detail_side: only {max(lo, hi)} vertices at the {axis} sides"
        if r < float(p["min_ratio"]):
            return None, f"detail_side: vertex counts {c} give no side with {p['min_ratio']}x more detail"
        if r < float(p["dominance"]) * other:
            return None, f"detail_side: x ratio {rx:.2f} and y ratio {ry:.2f} do not single out one axis"
        front = _axis_name(axis, 1 if hi > lo else -1)
        return front, f"detail_side: {max(lo, hi)} vs {min(lo, hi)} vertices in the {axis} slabs: front {front}"
    if rule == "open_side":
        p = rules["open_side"]
        f = stats["panel_fraction"]
        decisive = []
        for axis in ("x", "y"):
            a, b = f[f"-{axis}"], f[f"+{axis}"]
            hi, lo = max(a, b), min(a, b)
            if hi >= float(p["min_panel"]) and lo <= float(p["max_open_share"]) * hi:
                decisive.append((axis, 1 if b > a else -1, hi, lo))
        if len(decisive) != 1:
            return None, f"open_side: panel fractions {f} give {len(decisive)} axes with one closed side"
        axis, back, hi, lo = decisive[0]
        front = _axis_name(axis, -back)
        return front, (f"open_side: closed panel {hi:.2f} at {_axis_name(axis, back)}, {lo:.2f} at the other side: "
                       f"front {front}")
    raise ValueError(f"unknown front rule {rule!r}")


def view_direction(side: str, elevation_deg: float, azimuth_offset_deg: float = 0.0) -> tuple[float, float, float]:
    """Unit vector from the model centre toward a camera (or light) on ``side`` (``-Y``, ``+X``, ``+Y``,
    ``-X``), ``elevation_deg`` above the horizontal, turned ``azimuth_offset_deg`` counter-clockwise (from above)."""
    hx, hy = {"-Y": (0.0, -1.0), "+X": (1.0, 0.0), "+Y": (0.0, 1.0), "-X": (-1.0, 0.0)}[side]
    a = math.radians(azimuth_offset_deg)
    hx, hy = hx * math.cos(a) - hy * math.sin(a), hx * math.sin(a) + hy * math.cos(a)
    e = math.radians(elevation_deg)
    return (math.cos(e) * hx, math.cos(e) * hy, math.sin(e))


def view_location(centre, dist: float, side: str, elevation_deg: float) -> tuple[float, float, float]:
    d = view_direction(side, elevation_deg)
    return (centre[0] + dist * d[0], centre[1] + dist * d[1], centre[2] + dist * d[2])


def camera_distance(extents, lens_mm: float, sensor_mm: float = 36.0, margin: float = 1.08) -> float:
    """Distance at which the box's bounding sphere fills a square frame of a ``lens_mm`` camera."""
    radius = 0.5 * math.sqrt(sum(float(e) ** 2 for e in extents))
    half_fov = math.atan(0.5 * sensor_mm / lens_mm)
    return max(radius, 1e-6) / math.sin(half_fov) * margin


# --------------------------------------------------------------------------
# Unit guess and type (§7.2)
# --------------------------------------------------------------------------

def _inside(v: float, lo: float, hi: float, tol: float) -> bool:
    return lo / (1.0 + tol) <= v <= hi * (1.0 + tol)


def fits_type(dims, ftype: str, table: dict, tol: float, heights: dict) -> bool:
    """Footprint in the size-table range (either orientation, ``tol`` on top) and height in the type's range."""
    if ftype not in table or ftype not in heights:
        return False
    a, b, h = (float(v) for v in dims)
    (w0, w1), (d0, d1) = table[ftype]
    foot = ((_inside(a, w0, w1, tol) and _inside(b, d0, d1, tol))
            or (_inside(a, d0, d1, tol) and _inside(b, w0, w1, tol)))
    h0, h1 = heights[ftype]
    return foot and float(h0) <= h <= float(h1)


def _fmt_dims(dims) -> str:
    return " x ".join(f"{float(v):.3g}" for v in dims)


def guess_unit(extents_raw, types, cfg: dict, table: dict, tol: float) -> dict:
    """The unit factor of §7.2 and the resolved type.

    ``{"ok": True, "scale", "type", "dims_m", "note", "fits": [...]}`` when exactly one factor of ``cfg["units"]``
    puts the box (x, y extents as the footprint, z as the height) in the range of one of ``types``; otherwise
    ``{"ok": False, "code": "unit_none" | "unit_ambiguous" | "size_range", "detail", "fits"}``. A bed group is
    split by the width (shorter side) at ``bed_split_width_m``.

    When no factor fits, the model's units are unknown (prep pod 3 Oct 2026: 86 of 127 candidates, e.g. an
    armchair of 353 x 441 x 514 raw): ``normalise_unit`` scales it to the type's typical size instead, and only its
    proportions decide (``"normalised": True``)."""
    heights = {t: spec["height"] for t, spec in cfg["types"].items()}
    fits = []
    for factor in cfg["units"]:
        dims = [float(e) * float(factor) for e in extents_raw]
        ok = [t for t in types if fits_type(dims, t, table, tol, heights)]
        if ok:
            fits.append({"scale": float(factor), "types": ok, "dims_m": [round(v, 4) for v in dims]})
    if not fits:
        return normalise_unit(extents_raw, types, cfg, table, tol)
    if len(fits) > 1:
        return {"ok": False, "code": "unit_ambiguous", "fits": fits,
                "detail": "factors " + ", ".join(f"x{f['scale']:g} ({_fmt_dims(f['dims_m'])} m)" for f in fits)
                          + " all fit"}
    fit = fits[0]
    dims = fit["dims_m"]
    if set(types) == {"bed_single", "bed_double"}:
        width = min(dims[0], dims[1])
        split = float(cfg["bed_split_width_m"])
        ftype = "bed_single" if width <= split else "bed_double"
        note = f"bed width {width:.2f} m {'<=' if ftype == 'bed_single' else '>'} {split} m: {ftype}"
    else:
        ftype = types[0]
        note = ""
    if ftype not in fit["types"]:
        return {"ok": False, "code": "size_range", "fits": fits,
                "detail": f"{_fmt_dims(dims)} m is a {ftype} by width but outside its size range"}
    unit_note = f"x{fit['scale']:g}: {_fmt_dims(extents_raw)} (raw) -> {_fmt_dims(dims)} m in the {ftype} range"
    return {"ok": True, "scale": fit["scale"], "type": ftype, "dims_m": dims, "fits": fits,
            "note": unit_note + (f"; {note}" if note else "")}


NORMALISED_NOTE = "normalised by type (model units unknown)"


def shape_scales(extents_raw, ftype: str, table: dict, tol: float, heights: dict) -> list[tuple[float, float]]:
    """The scale intervals ``[(lo, hi), ...]`` (one per footprint orientation) that put the raw box in the type's
    size range (``fits_type``: footprint with ``tol``, height). Empty when the box's proportions (footprint
    width / depth, height / width) are outside the type's ranges, whatever its unit."""
    if ftype not in table or ftype not in heights:
        return []
    x, y, z = (float(v) for v in extents_raw)
    (w0, w1), (d0, d1) = table[ftype]
    h0, h1 = (float(v) for v in heights[ftype])
    k = 1.0 + tol
    out = []
    for a, b in ((x, y), (y, x)):
        lo = max(w0 / k / a, d0 / k / b, h0 / z)
        hi = min(w1 * k / a, d1 * k / b, h1 / z)
        if lo <= hi:
            out.append((lo, hi))
    return out


def normalise_unit(extents_raw, types, cfg: dict, table: dict, tol: float) -> dict:
    """The unit guess of a model whose units are unknown (no factor of ``cfg["units"]`` fits).

    ``unit_scale`` = the type's typical footprint size (the size table centre, geometric mean of width and depth)
    / the raw footprint size (geometric mean of x and y), moved to the nearest scale that keeps the box in the
    type's range when the centre would not (it exists exactly when the proportions fit). The refusal rule is the
    proportions (``shape_scales``): footprint width / depth and height / width in the type's ranges, else
    ``unit_none``. A bed group is split by its proportions (width / length times a typical bed length, against
    ``bed_split_width_m``), as the absolute width is unknown. The note starts with ``NORMALISED_NOTE``; the fit
    scales every model to the drawn footprint anyway."""
    heights = {t: spec["height"] for t, spec in cfg["types"].items()}
    raw = [float(v) for v in extents_raw]
    factors = ", ".join(f"x{f:g}" for f in cfg["units"])
    if len(raw) != 3 or not all(math.isfinite(v) and v > 0 for v in raw):
        return {"ok": False, "code": "unit_none", "fits": [], "detail": f"no usable box ({_fmt_dims(raw)} raw)"}
    shapes = {t: shape_scales(raw, t, table, tol, heights) for t in types}
    note = ""
    if set(types) == {"bed_single", "bed_double"}:
        long_side = sum(sum(table[t][1]) / 2.0 for t in types) / len(types)      # depth centres: bed length
        ratio = min(raw[0], raw[1]) / max(raw[0], raw[1])
        width = ratio * long_side
        split = float(cfg["bed_split_width_m"])
        ftype = "bed_single" if width <= split else "bed_double"
        note = (f"bed width {width:.2f} m from the proportions (width / length {ratio:.3f} x a typical bed length "
                f"{long_side:.3f} m) {'<=' if ftype == 'bed_single' else '>'} {split} m: {ftype}")
        if not shapes[ftype]:
            other = [t for t in types if t != ftype and shapes[t]]
            code = "size_range" if other else "unit_none"
            return {"ok": False, "code": code, "fits": [],
                    "detail": f"no factor ({factors}) fits {_fmt_dims(raw)} (raw), and its proportions are not a "
                              f"{ftype}'s ({note})"}
    else:
        fitting = [t for t in types if shapes[t]]
        if not fitting:
            return {"ok": False, "code": "unit_none", "fits": [],
                    "detail": f"no factor ({factors}) puts {_fmt_dims(raw)} (raw) in the {'/'.join(types)} range, "
                              f"and its proportions (footprint, height / width) are outside it at any scale"}
        if len(fitting) > 1:
            return {"ok": False, "code": "unit_ambiguous", "fits": [],
                    "detail": f"units unknown and the proportions fit {', '.join(fitting)}"}
        ftype = fitting[0]
    (w0, w1), (d0, d1) = table[ftype]
    wc, dc = (w0 + w1) / 2.0, (d0 + d1) / 2.0
    centre = math.sqrt(wc * dc / (raw[0] * raw[1]))
    intervals = shapes[ftype]
    scale, moved = centre, ""
    if not any(lo <= centre <= hi for lo, hi in intervals):
        ends = [(lo * (1.0 + 1e-9), "lo") for lo, _ in intervals] + [(hi * (1.0 - 1e-9), "hi") for _, hi in intervals]
        scale = min(ends, key=lambda e: abs(e[0] - centre))[0]
        moved = f", moved from x{centre:.6g} to keep the box in the {ftype} range"
    dims_raw = [v * scale for v in raw]
    if not fits_type(dims_raw, ftype, table, tol, heights):                    # guards the arithmetic above
        return {"ok": False, "code": "unit_none", "fits": [],
                "detail": f"normalised box {_fmt_dims(dims_raw)} m is outside the {ftype} range"}
    dims = [round(v, 4) for v in dims_raw]
    unit_note = (f"{NORMALISED_NOTE}: no factor ({factors}) fits {_fmt_dims(raw)} (raw); x{scale:.6g} scales the "
                 f"raw footprint to the typical {ftype} footprint (size table centre {wc:g} x {dc:g} m){moved}: "
                 f"{_fmt_dims(dims)} m; its proportions are in the {ftype} range")
    return {"ok": True, "scale": scale, "type": ftype, "dims_m": dims, "fits": [], "normalised": True,
            "note": unit_note + (f"; {note}" if note else "")}


def known_unit(extents_raw, ftype: str, cfg: dict, table: dict, tol: float, source: str = "") -> dict:
    """The unit of a record whose units are known (``units_known``: ABO, metres; docs/milestone8.md §2): scale 1,
    the survey's type, refused ``size_range`` when the measured box is outside the type's range (never normalised).
    """
    dims = [round(float(v), 4) for v in extents_raw]
    where = f"{source} metadata" if source else "the source"
    if fits_type(dims, ftype, table, tol, heights_of(cfg)):
        return {"ok": True, "scale": 1.0, "type": ftype, "dims_m": dims, "fits": [], "known": True,
                "note": f"units known (metres, {where}): {_fmt_dims(dims)} m in the {ftype} range"}
    return {"ok": False, "code": "size_range", "fits": [], "known": True,
            "detail": f"units known (metres, {where}): {_fmt_dims(dims)} m is outside the {ftype} range "
                      "(never normalised)"}


# --------------------------------------------------------------------------
# 2. Thumbnails: Blender jobs, the 2 x 2 sheet, thumbnails.json
# --------------------------------------------------------------------------

def blender_command(blender: str, jobs_path: Path) -> list[str]:
    """``blender -b --factory-startup --python-exit-code 1 --python <this file> -- blender-thumbs <jobs>``."""
    return [str(blender), "-b", "--factory-startup", "--python-exit-code", "1", "--python",
            str(Path(__file__).resolve()), "--", "blender-thumbs", str(jobs_path)]


def run_blender(blender: str, jobs_path: Path, log_path: Path, timeout: float) -> int:
    """Run the Blender side; the full output goes to ``log_path``. Returns Blender's exit code."""
    cmd = blender_command(blender, jobs_path)
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=max(60.0, float(timeout)))
    except subprocess.TimeoutExpired as exc:
        Path(log_path).write_text(f"$ {' '.join(cmd)}\n\ntimeout after {exc.timeout} s\n", encoding="utf-8")
        return EXIT_DEADLINE
    Path(log_path).write_text(f"$ {' '.join(cmd)}\n\n{proc.stdout}\n--- stderr ---\n{proc.stderr}", encoding="utf-8")
    return proc.returncode


def _measure_paths(work: Path, uid: str) -> tuple[Path, list[Path]]:
    return work / "measure" / f"{uid}.json", [work / "views" / f"{uid}_{i}.png" for i in range(len(VIEW_SIDES))]


def _measure_done(measure_path: Path, sha: str, views: list[Path]) -> bool:
    rec = read_json(measure_path)
    return bool(rec and rec.get("glb_sha256") == sha and rec.get("ok") and all(v.is_file() for v in views))


def needs_deck(cand: dict) -> bool:
    """A bed candidate: the thumbnail step measures its deck (docs/milestone8.md §2)."""
    return any(t in BED_TYPES for t in cand.get("types") or [])


def pixels_sha256(path: Path) -> dict:
    """sha256 and shape of the decoded RGB pixels of an image (what the judge sees; independent of the encoder's
    metadata)."""
    import numpy as np
    from PIL import Image
    arr = np.ascontiguousarray(np.asarray(Image.open(path).convert("RGB"), dtype=np.uint8))
    return {"sha256": hashlib.sha256(arr.tobytes()).hexdigest(), "shape": list(arr.shape)}


def compose_sheet(view_paths: list[Path], sheet_path: Path, thumb_path: Optional[Path], settings: dict,
                  comment: Optional[str] = None) -> dict:
    """The 2 x 2 judging sheet (tiles in ``VIEW_SIDES`` order: top left, top right, bottom left, bottom right,
    each numbered 0..3 with cv2's Hershey font, no anti-aliasing) as JPEG, and the scaled-down thumbnail.
    Returns the sheet's ``pixels_sha256``."""
    import cv2
    import numpy as np
    from PIL import Image

    res = int(settings["resolution"])
    sheet = np.zeros((2 * res, 2 * res, 3), dtype=np.uint8)
    for i, path in enumerate(view_paths):
        img = Image.open(path).convert("RGB")
        if img.size != (res, res):
            img = img.resize((res, res), Image.LANCZOS)
        r, c = divmod(i, 2)
        sheet[r * res:(r + 1) * res, c * res:(c + 1) * res] = np.asarray(img, dtype=np.uint8)
    sheet = np.ascontiguousarray(sheet)
    for i in range(len(view_paths)):
        r, c = divmod(i, 2)
        x, y = c * res, r * res
        cv2.rectangle(sheet, (x + 4, y + 4), (x + 30, y + 34), (255, 255, 255), -1, cv2.LINE_8)
        cv2.putText(sheet, str(i), (x + 9, y + 29), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2, cv2.LINE_8)
    sheet[res - 1:res + 1, :] = 40
    sheet[:, res - 1:res + 1] = 40
    sheet_path = Path(sheet_path)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = sheet_path.with_name(sheet_path.name + ".tmp.jpg")
    Image.fromarray(sheet).save(tmp, format="JPEG", quality=int(settings.get("sheet_jpeg_quality", 90)))
    tmp.replace(sheet_path)
    if thumb_path is not None:
        px = int(settings.get("thumb_px", 256))
        thumb = Image.fromarray(sheet).resize((px, px), Image.LANCZOS)
        thumb_path = Path(thumb_path)
        thumb_path.parent.mkdir(parents=True, exist_ok=True)
        kwargs = {"format": "JPEG", "quality": int(settings.get("thumb_jpeg_quality", 85))}
        if comment:
            kwargs["comment"] = comment.encode("utf-8")
        try:
            thumb.save(thumb_path, **kwargs)
        except TypeError:                      # an old Pillow without the JPEG comment argument
            kwargs.pop("comment", None)
            thumb.save(thumb_path, **kwargs)
    return pixels_sha256(sheet_path)


def odc_by_notice(cfg: Optional[dict] = None) -> str:
    """The ODC-By 1.0 §4.2 notice carried by every library output that holds Objaverse data (§7.3)."""
    ds = (cfg or {}).get("dataset") or {"repo": "allenai/objaverse",
                                        "revision": "21e4e142159e2153706c23a3a02e55cec5591cea",
                                        "page": "https://huggingface.co/datasets/allenai/objaverse",
                                        "licence_url": "https://opendatacommons.org/licenses/by/1-0/"}
    page = ds.get("page") or f"https://huggingface.co/datasets/{ds['repo']}"
    return (f"Contains information from Objaverse 1.0 ({page}, "
            f"revision {ds['revision'][:7]}), which is made available under the ODC Attribution License "
            f"(ODC-By 1.0, {ds.get('licence_url', 'https://opendatacommons.org/licenses/by/1-0/')}). Every object "
            "keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY "
            "4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. "
            "This file is licensed ODC-By 1.0, not MIT.")


def attribution_line(title: str, author: str, source_url: str, licence: str, cfg: Optional[dict] = None) -> str:
    """The credit line of §7.3 (CC BY 4.0; the same form names CC0 1.0 for a CC0 object and every flagged licence
    of objaverse.yaml by its printed name)."""
    cfg = cfg or {}
    lic = cfg.get("licences") or {}
    names = lic.get("names") or {CC0: "CC0 1.0", CC_BY: "CC BY 4.0"}
    urls = lic.get("urls") or {CC0: "https://creativecommons.org/publicdomain/zero/1.0/",
                               CC_BY: "https://creativecommons.org/licenses/by/4.0/"}
    att = cfg.get("attribution") or {"via": "Objaverse (allenai/objaverse, ODC-By 1.0)",
                                     "changes": "scaled to the drawn footprint, re-oriented, rendered, AI-retouched"}
    name, url = names.get(licence, licence), urls.get(licence)
    shown = f"{name} ({url})" if url else name
    return f'"{title}" by {author} ({source_url}), {shown}, via {att["via"]}; changes: {att["changes"]}'


def _thumb_settings(cfg: dict, device: str) -> dict:
    s = dict(cfg["thumbnails"])
    s["views"] = list(VIEW_SIDES)
    s["device"] = device
    rules = cfg["front_rules"]
    s["top_fraction"] = float(rules["top_fraction"])
    s["side_fraction"] = float(rules["side_fraction"])
    s["normal_dot"] = float(rules["open_side"]["normal_dot"])
    s["deck_ray_offset"] = float((cfg.get("bed_frame") or {}).get("ray_offset", 0.2))
    return s


def thumbnails(out: Path, work: Optional[Path] = None, cfg: Optional[dict] = None, blender: Optional[str] = None,
               runner: Optional[Callable] = None, deadline: Optional[float] = None, device: str = "auto",
               log: Callable = print) -> tuple[dict, int]:
    """§7.2 thumbnails for every downloaded candidate of every survey file (``load_candidates``) ->
    ``thumbnails.json`` and the exit code.

    Objects measured and rendered earlier (same GLB sha256, four views on disk) are not rendered again; a bed
    measured before Milestone 8 (no deck) is measured once more without rendering. A record with ``units_known``
    keeps its type and scale 1 (``known_unit``: refused when outside the type's range); the others go through the
    unit guess. ``runner(blender, jobs_path, log_path, timeout) -> exit code`` replaces ``run_blender`` (tests)."""
    cfg = cfg or load_config()
    out = Path(out)
    work = Path(work) if work else out / WORK_DIR
    cands = [c for c in load_candidates(out) if c.get("glb")]
    # A uid that is not a plain id (the cache path models/<source>/<uid>.glb and the fetch need one, e.g. a
    # generated uid with a space) is refused here, visibly, instead of failing at the full run's fetch.
    bad_uids = [c for c in cands if not _UID_RE.fullmatch(str(c["uid"]))]
    cands = [c for c in cands if _UID_RE.fullmatch(str(c["uid"]))]
    settings = _thumb_settings(cfg, device)
    jobs = []
    for cand in cands:
        measure, views = _measure_paths(work, cand["uid"])
        deck = needs_deck(cand)
        job = {"uid": cand["uid"], "glb": cand["glb"], "glb_sha256": cand["glb_sha256"], "measure": str(measure),
               "views": [str(v) for v in views], "deck": deck, "render": True}
        if _measure_done(measure, cand["glb_sha256"], views):
            if not deck or "deck" in (read_json(measure) or {}):
                continue
            job["render"] = False                       # measured before M8: the deck only, the views stay
        jobs.append(job)
    rc = EXIT_OK
    if jobs:
        for sub in ("measure", "views"):
            (work / sub).mkdir(parents=True, exist_ok=True)
        jobs_doc = {"settings": settings, "deadline": deadline, "work": str(work), "objects": jobs}
        jobs_path = write_json(work / "blender_jobs.json", jobs_doc)
        if runner is None:
            if blender is None:
                from wenart.blender.cli import find_blender
                blender = find_blender()
            if blender is None:
                raise UsageError("no Blender binary: set WENART_BLENDER or pass --blender")
            runner = run_blender
        timeout = (deadline - time.time() + 120.0) if deadline else 3.0 * 3600.0
        log(f"library thumbnails: rendering {sum(j['render'] for j in jobs)} object(s), measuring "
            f"{sum(not j['render'] for j in jobs)} deck(s) only, in one Blender process")
        rc = runner(blender, jobs_path, work / "blender.log", timeout)
        log(f"library thumbnails: Blender exited {rc}")
    status = read_json(work / "blender_status.json") or {}

    table, tol = library_size_table(cfg)
    rules = cfg["front_rules"]
    objects: dict[str, dict] = {}
    notices = []
    by_uid = {c["uid"]: c for c in cands}
    for cand in cands:
        uid = cand["uid"]
        measure_path, views = _measure_paths(work, uid)
        rec = {"uid": uid, "group": cand["group"], "types": cand["types"], "title": cand.get("title"),
               "author": cand.get("author"), "source_url": cand.get("source_url"), "licence": cand.get("licence"),
               "source": cand["source"], "licence_flag": cand.get("licence_flag"), "kind": cand["kind"],
               "decor_type": cand.get("decor_type"), "units_known": bool(cand.get("units_known"))}
        objects[uid] = rec
        m = read_json(measure_path)
        if not m or m.get("glb_sha256") != cand["glb_sha256"]:
            rec.update(status="refused", code="not_rendered",
                       detail=f"Blender exit {rc}" if rc else "no measurement written")
            continue
        if not m.get("ok"):
            rec.update(status="refused", code="blender_error", detail=str(m.get("error") or "")[:300])
            continue
        if not all(v.is_file() for v in views):
            rec.update(status="refused", code="blender_error", detail="views missing")
            continue
        if needs_deck(cand) and "deck" not in m:
            rec.update(status="refused", code="not_rendered", detail="deck not measured (Blender stopped before it)")
            continue
        st = m["stats"]
        rec["measure"] = {k: m.get(k) for k in ("vertices", "triangles", "mesh_objects", "images",
                                                "colour_attributes", "seconds")}
        rec["measure"].update({"bbox_min_raw": st["bbox_min"], "bbox_max_raw": st["bbox_max"],
                               "extents_raw": st["extents"]})
        rec["stats"] = {k: st[k] for k in ("top_centroid_n", "side_counts", "panel_fraction")}
        if cand.get("units_known"):
            unit = known_unit(st["extents"], cand["types"][0], cfg, table, tol, cand["source"])
        else:
            unit = guess_unit(st["extents"], cand["types"], cfg, table, tol)
        rec["unit"] = unit
        if not unit["ok"]:
            rec.update(status="refused", code=unit["code"], detail=unit["detail"])
            continue
        ftype = unit["type"]
        rule = cfg["types"][ftype]["front"]
        front, note = geometric_front(st, rule, rules)
        rec.update(status="ready", type=ftype, front_rule=rule, geometric_front=front, geometric_note=note,
                   rank=cand.get("rank"))
        if cand.get("front_documented") and rule != FRONTLESS_RULE:
            rec["front_documented"] = cand["front_documented"]
            rec["front_documented_note"] = cand.get("front_note") or f"{cand['source']} documents the front"
        if ftype in BED_TYPES:
            deck = m.get("deck") or {}
            rec["deck"] = deck
            height = deck.get("height_raw")
            rec["deck_height_m"] = round(float(height) * float(unit["scale"]), 4) if height is not None else None

    # <= per_type_limit per source and resolved type (a category that maps to two types, ``bed``, was surveyed with
    # the limit of both; the split by width may give one of them more): the best survey ranks stay.
    limit = int(cfg["prefilter"]["per_type_limit"])
    by_type: dict[tuple, list[dict]] = {}
    for rec in objects.values():
        if rec["status"] == "ready":
            by_type.setdefault((rec["source"], rec["type"]), []).append(rec)
    for (source, ftype), recs in by_type.items():
        for n, rec in enumerate(sorted(recs, key=lambda r: (r.get("rank") or 0, r["uid"]))):
            if n >= limit:
                rec.update(status="refused", code="over_candidate_limit",
                           detail=f"survey rank {rec.get('rank')}: {source} has {len(recs)} {ftype} candidates "
                                  f"after the unit guess, {limit} are judged")
    for uid, rec in objects.items():
        if rec["status"] != "ready":
            continue
        cand = by_uid[uid]
        sheet_rel = f"{JUDGE_DIR}/{SHEETS_DIR}/{uid}.jpg"
        thumb_rel = f"{THUMBS_DIR}/{rec['type']}/{uid}.jpg"
        line = credit_line(cand, cfg)
        rec["sheet_pixels"] = compose_sheet(_measure_paths(work, uid)[1], out / sheet_rel, out / thumb_rel,
                                            settings, comment=f"{cand['source']} {uid}: {line}")
        rec.update(sheet=sheet_rel, thumb=thumb_rel)
        notices.append((thumb_rel, line, cand["source"]))

    for cand in bad_uids:
        objects[cand["uid"]] = {"uid": cand["uid"], "group": cand["group"], "types": cand["types"],
                                "source": cand["source"], "kind": cand["kind"], "status": "refused", "code": "bad_uid",
                                "detail": "letters, digits, _ and - only (1-64): the cache path needs a plain id"}
    counts: dict[str, int] = {}
    for rec in objects.values():
        key = rec["status"] if rec["status"] == "ready" else rec["code"]
        counts[key] = counts.get(key, 0) + 1
    # ``blender_status.json`` is the last Blender run's (a resumed run that renders nothing keeps the earlier one).
    doc = {"schema_version": SCHEMA_VERSION, "kind": "objaverse_thumbnails", "generated_utc": now_utc(),
           "sources": sorted({c["source"] for c in cands}),
           "device": status.get("device"), "blender": status.get("blender"), "blender_exit": rc,
           "rendered_now": sum(1 for j in jobs if j["render"]), "decks_now": sum(1 for j in jobs if j["deck"]),
           "settings": settings, "counts": dict(sorted(counts.items())), "objects": objects}
    write_json(out / THUMBS_JSON, doc)
    _write_thumb_notice(out, notices, cfg)
    if rc == EXIT_DEADLINE:
        return doc, EXIT_DEADLINE
    if rc != EXIT_OK or counts.get("not_rendered"):
        return doc, EXIT_FAIL
    return doc, EXIT_OK


GENERATED_NOTICE = ("Generated models (docs/milestone8.md §3): made by TRELLIS.2-4B (microsoft/TRELLIS.2-4B, MIT) "
                    "from Z-Image-Turbo product images; marked `generated`, no third-party credit.")


def source_notices(sources, cfg: Optional[dict] = None) -> list[str]:
    """The notices of the sources present: the ODC-By notice (Objaverse), the ABO credit (CC BY 4.0) and the
    generated-model note."""
    out = []
    if "objaverse" in sources:
        out.append(odc_by_notice(cfg))
    if "abo" in sources:
        from wenart.assets import abo
        out.append(abo.notice())
    if "generated" in sources:
        out.append(GENERATED_NOTICE)
    return out


def _write_thumb_notice(out: Path, notices: list[tuple[str, str, str]], cfg: dict) -> None:
    sources = sorted({source for _rel, _line, source in notices}, key=SOURCE_ORDER.index)
    lines = ["# Thumbnails of library models", ""]
    for text in source_notices(sources or ["objaverse"], cfg):
        lines += [text, ""]
    lines += ["Each thumbnail is a render of the object (changed: re-framed, re-lit, rendered); credits:", ""]
    lines += [f"- `{rel}`: {line}" for rel, line, _source in sorted(notices)]
    path = out / THUMBS_DIR / NOTICE_NAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# 3./4. Judging: schema, prompt, requests, answers (the recognition answer-store format)
# --------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You judge 3D furniture models for a photoreal interior renderer and answer only with JSON that follows the "
    "given schema. Judge only what is visible in the images. When unsure, answer false or null."
)

# Type -> (name, what it is) for the question.
TYPE_WORDS: dict[str, tuple[str, str]] = {
    "bed_double": ("double bed", "a bed for two people, about 1.4 to 2.0 m wide"),
    "bed_single": ("single bed", "a bed for one person, about 0.8 to 1.2 m wide"),
    "sofa": ("sofa", "a couch for two or more people"),
    "armchair": ("armchair", "an upholstered easy chair for one person, with arms"),
    "chair": ("chair", "a single dining or side chair"),
    "table_dining": ("dining table", "a table for meals, seating four or more"),
    "table_coffee": ("coffee table", "a low table in front of a sofa"),
    "desk": ("desk", "a writing or computer desk"),
    "wardrobe": ("wardrobe", "a tall free-standing clothes cupboard with doors"),
    "bookshelf": ("bookshelf", "a free-standing bookcase or shelving unit"),
    "nightstand": ("nightstand", "a small bedside cabinet or table"),
    "dresser": ("chest of drawers", "a waist-high chest of drawers or dresser"),
    "toilet": ("toilet", "a toilet pan, with or without its cistern"),
    "washbasin": ("washbasin", "a bathroom wash basin, on a pedestal, wall-hung or on a vanity unit"),
    "bathtub": ("bathtub", "a bath tub"),
    "fridge": ("refrigerator", "a free-standing fridge or fridge-freezer"),
    "stove": ("kitchen stove", "a free-standing cooker or range with a hob"),
    "floor_lamp": ("floor lamp", "a standing lamp on the floor, about 1.4 to 1.9 m tall"),
    "potted_plant": ("potted plant", "an indoor plant in a pot"),
}
STYLE_HINTS: dict[str, str] = {
    "scandinavian": "light wood, white, simple and cosy",
    "japandi": "low, natural wood, calm and minimal",
    "modern minimal": "plain flat surfaces, no ornament",
    "minimal": "plain flat surfaces, no ornament",
    "modern": "clean contemporary lines",
    "industrial": "metal, raw wood, dark tones",
    "mediterranean": "terracotta, rattan, whitewashed wood",
    "classic": "traditional, carved, tufted or turned details",
    "rustic": "rough natural wood, farmhouse",
    "neutral": "plain enough to fit any style",
}
FRONT_WORDS = ("the seat side of a sofa or chair, the foot end of a bed, the doors or drawers of a cabinet, the open "
               "side of a shelf, the user side of a desk, toilet, washbasin, bath, stove or fridge")


# Decor type -> (name, what it is, what counts as one) for the decor question (docs/milestone8.md §2: "a rug is a rug,
# a planter holds a plant").
DECOR_WORDS: dict[str, tuple[str, str, str]] = {
    "cushion": ("cushion", "a decorative throw pillow or cushion for a sofa, chair or bed",
                "one throw pillow or cushion (not a seat pad, not a bed pillow, not a pouf)"),
    "plant": ("potted plant", "an indoor plant in a pot or planter",
              "a pot or planter that holds a plant with leaves; an empty pot, planter or vase is not one"),
    "rug": ("rug", "a floor rug or carpet", "one flat floor rug or carpet (not a doormat, not a wall hanging)"),
    "wall_art": ("wall art", "a framed picture, print, canvas or mural for a wall",
                 "one picture, print, canvas or mural for a wall (not a mirror, not a shelf, not a clock)"),
    # Milestone 9 decor types (docs/milestone9.md §3).
    "vase": ("vase", "a decorative vase for a table, a sideboard or a shelf",
             "one vase, empty or with flowers or branches (not a planter with soil, not a bowl, not a lamp)"),
    "bowl": ("decorative bowl", "a decorative bowl or tray for a table or a sideboard",
             "one bowl or tray, empty or with fruit (not a vase, not a pot, not a plate stack)"),
    "plant_small": ("small potted plant", "a small indoor plant in a pot for a table or a shelf",
                    "a small pot that holds a plant with leaves; an empty pot, planter or vase is not one"),
    "table_lamp": ("table lamp", "a lamp that stands on a table, a desk or a nightstand",
                   "one table or desk lamp with its shade or head (not a floor lamp, not a wall or ceiling light)"),
    "mirror": ("wall mirror", "a mirror that hangs on a wall",
               "one wall mirror with or without a frame (not a floor or leaner mirror, not a mirror cabinet)"),
}
# The side a front-facing decor type shows (the M8 wall art question keeps its words, so its answers stay current).
DECOR_FRONT_WORDS: dict[str, str] = {"wall_art": "the picture side", "mirror": "the mirror side"}
TYPE_WORDS.update({
    "side_table": ("side table", "a small table beside a sofa, an armchair or a bed"),
    "tv_unit": ("TV unit", "a low cabinet or stand for a television"),
    # The types the generator fills (M8 pod L3: judge-requests raised KeyError 'shower').
    "washing_machine": ("washing machine", "a front-loading washing machine or washer-dryer"),
    "sink_kitchen": ("kitchen sink unit", "a kitchen base cabinet with a sink and a tap"),
    "shower": ("shower enclosure", "a walk-in or framed shower enclosure on its tray"),
})


def item_kind(item: dict) -> str:
    """The kind of a judging request item (``furniture`` unless its context says ``decor``)."""
    return str((item.get("context") or {}).get("kind") or "furniture")


def judge_schema(kind: str = "furniture") -> dict:
    """The §7.2 answer schema (strict: no other keys). No ``uniqueItems`` on ``styles``: vLLM's xgrammar backend
    does not implement it (every judge call of the 3 Oct 2026 prep pod failed with HTTP 400 "Unimplemented keys:
    uniqueItems"); repeated styles are removed in code (``clean_judgement``). Decor (docs/milestone8.md §2) answers
    ``is_decor_type`` instead of ``matches_type`` and has no ``has_mattress``."""
    styles = list(style_values())
    props = {
        "is_single_object": {"type": "boolean"},
        "matches_type": {"type": "boolean"},
        "photoreal_quality": {"type": "integer", "minimum": 1, "maximum": 5},
        "has_mattress": {"type": ["boolean", "null"]},
        "styles": {"type": "array", "items": {"enum": styles}, "maxItems": len(styles)},
        "front_view": {"type": ["integer", "null"], "minimum": 0, "maximum": len(VIEW_SIDES) - 1},
    }
    required = ["is_single_object", "matches_type", "photoreal_quality", "has_mattress", "styles", "front_view"]
    title = "LibraryJudge"
    if kind == "decor":
        props = {"is_single_object": props["is_single_object"], "is_decor_type": {"type": "boolean"},
                 "photoreal_quality": props["photoreal_quality"], "styles": props["styles"],
                 "front_view": props["front_view"]}
        required = ["is_single_object", "is_decor_type", "photoreal_quality", "styles", "front_view"]
        title = "LibraryJudgeDecor"
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": title,
        "type": "object",
        "additionalProperties": False,
        "required": required,
        "properties": props,
    }


def judgement_errors(data, kind: str = "furniture") -> list[str]:
    import jsonschema
    validator = jsonschema.Draft202012Validator(judge_schema(kind))
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))]


def valid_judgement(data, kind: str = "furniture") -> bool:
    return data is not None and not judgement_errors(data, kind)


def clean_judgement(data):
    """A judge answer with ``styles`` de-duplicated (first mention kept; the schema cannot forbid repeats, see
    ``judge_schema``); anything else unchanged (None stays None)."""
    if not isinstance(data, dict) or not isinstance(data.get("styles"), list):
        return data
    styles: list = []
    for v in data["styles"]:
        if v not in styles:
            styles.append(v)
    return dict(data, styles=styles)


def _tiles_and_size(dims_m, normalised: bool, name: str) -> tuple[str, str]:
    tiles = ", ".join(f"{i} ({place}) from the model's {side} side"
                      for i, (place, side) in enumerate(zip(VIEW_PLACES, VIEW_SIDES)))
    size = (f"The tiles are framed on the model, so they do not show its size, and the model file gives no usable "
            f"unit: scaled to a typical {name} it would measure about {_fmt_dims(dims_m)} m (x, y, height)."
            if normalised else
            f"The tiles are framed on the model, so they do not show its size: it measures about "
            f"{_fmt_dims(dims_m)} m (x, y, height).")
    return tiles, size


def judge_prompt(ftype: str, dims_m, has_front: bool, normalised: bool = False) -> str:
    """The question for one object: the same text for both models (temperature 0, structured output). A model of
    unknown units (``normalised``) is not given a measured size: it is scaled to a typical piece of the type."""
    name, what = TYPE_WORDS[ftype]
    tiles, size = _tiles_and_size(dims_m, normalised, name)
    styles = "; ".join(f"{s} ({STYLE_HINTS.get(s, s)})" for s in style_values())
    is_bed = ftype in BED_TYPES
    mattress = ("true when the bed has a mattress on it, false for a bare frame or base" if is_bed
                else "null (this is not a bed)")
    front = (f"the number of the tile that looks straight at the front of the piece ({FRONT_WORDS}); null when you "
             "cannot tell" if has_front else "null (this type has no front)")
    return "\n\n".join([
        "The image is a 2 x 2 sheet of four renders of one 3D model from an online model library, on a plain grey "
        "background. Each tile shows the model from one side, 30 degrees from above, and carries its number: "
        f"{tiles}. {size}",
        f"It is offered as a {name} ({what}) for photoreal renders of furnished rooms.",
        "Fields of the answer:\n"
        "- is_single_object: true when the tiles show exactly one piece and nothing else (no second piece, room, "
        "floor, rug, wall, person or text).\n"
        f"- matches_type: true when the piece is a {name}.\n"
        "- photoreal_quality: 1 to 5, how real it would look in a photoreal interior render: 5 detailed shape and "
        "realistic materials, 4 good, 3 plain or game-like, 2 crude, 1 broken, untextured or cartoon.\n"
        f"- has_mattress: {mattress}.\n"
        f"- styles: the interior styles the piece fits, from: {styles}. List only styles that clearly fit; an empty "
        "list when none does.\n"
        f"- front_view: {front}.",
        "Answer only with JSON.",
    ])


def decor_prompt(decor_type: str, dims_m, has_front: bool, normalised: bool = False) -> str:
    """The decor question (docs/milestone8.md §2): is it that decor type (a planter must hold a plant), single,
    photoreal, which styles, and for wall art the picture side."""
    name, what, counts = DECOR_WORDS[decor_type]
    tiles, size = _tiles_and_size(dims_m, normalised, name)
    styles = "; ".join(f"{s} ({STYLE_HINTS.get(s, s)})" for s in style_values())
    side = DECOR_FRONT_WORDS.get(decor_type, "the picture side")
    front = (f"the number of the tile that looks straight at {side}; null when you cannot tell" if has_front
             else "null (this decor has no front)")
    return "\n\n".join([
        "The image is a 2 x 2 sheet of four renders of one 3D model from an online model library, on a plain grey "
        "background. Each tile shows the model from one side, 30 degrees from above, and carries its number: "
        f"{tiles}. {size}",
        f"It is offered as {name} decor ({what}) for photoreal renders of furnished rooms.",
        "Fields of the answer:\n"
        "- is_single_object: true when the tiles show exactly one item and nothing else (no second item, room, "
        "floor, wall, person or text).\n"
        f"- is_decor_type: true when it is {counts}.\n"
        "- photoreal_quality: 1 to 5, how real it would look in a photoreal interior render: 5 detailed shape and "
        "realistic materials, 4 good, 3 plain or game-like, 2 crude, 1 broken, untextured or cartoon.\n"
        f"- styles: the interior styles it fits, from: {styles}. List only styles that clearly fit; an empty list "
        "when none does.\n"
        f"- front_view: {front}.",
        "Answer only with JSON.",
    ])


def has_front_of(ftype: str, cfg: dict) -> bool:
    return cfg["types"][ftype]["front"] != FRONTLESS_RULE


def request_item(rec: dict, out: Path, cfg: dict) -> dict:
    """One judging request (``judge/requests.json`` item) for a ``ready`` object of ``thumbnails.json``. The
    furniture question is the M7 one (answers of M7 objects stay current); decor gets ``decor_prompt`` and the decor
    schema."""
    ftype = rec["type"]
    kind = rec.get("kind") or "furniture"
    normalised = bool(rec["unit"].get("normalised"))
    if kind == "decor":
        prompt = decor_prompt(ftype, rec["unit"]["dims_m"], has_front_of(ftype, cfg), normalised)
    else:
        prompt = judge_prompt(ftype, rec["unit"]["dims_m"], has_front_of(ftype, cfg), normalised)
    image = f"{SHEETS_DIR}/{rec['uid']}.jpg"
    pixels = pixels_sha256(Path(out) / JUDGE_DIR / image)
    description = {"version": JUDGE_VERSION, "task": TASK, "system": SYSTEM_PROMPT, "prompt": prompt,
                   "schema": judge_schema(kind), "sheet": pixels}
    context = {"uid": rec["uid"], "type": ftype, "dims_m": rec["unit"]["dims_m"], "title": rec["title"],
               "source": rec.get("source") or SOURCE, "kind": kind}
    if kind == "decor":
        context["decor_type"] = rec.get("decor_type") or ftype
    return {"key": f"lib_{rec['uid']}", "task": TASK, "images": [image], "prompt": prompt, "context": context,
            "input_sha256": canonical_sha256(description)}


def judge_requests(out: Path, cfg: Optional[dict] = None) -> dict:
    """``judge/requests.json`` for every ``ready`` object (keys ``lib_<uid>``, in uid order)."""
    cfg = cfg or load_config()
    out = Path(out)
    thumbs = read_json(out / THUMBS_JSON)
    if thumbs is None:
        raise UsageError(f"{out / THUMBS_JSON} not found: run thumbnails first")
    items = [request_item(rec, out, cfg) for uid, rec in sorted(thumbs["objects"].items())
             if rec.get("status") == "ready"]
    doc = {"schema_version": SCHEMA_VERSION, "kind": "objaverse_judge_requests", "task": TASK,
           "judge_version": JUDGE_VERSION, "system_prompt": SYSTEM_PROMPT, "schema": judge_schema(),
           "schemas": {k: judge_schema(k) for k in ("furniture", "decor")},
           "view_sides": list(VIEW_SIDES), "items": items}
    write_json(out / JUDGE_DIR / REQUESTS_NAME, doc)
    return doc


def read_requests(out: Path) -> Optional[dict]:
    doc = read_json(Path(out) / JUDGE_DIR / REQUESTS_NAME)
    if doc is not None and doc.get("kind") != "objaverse_judge_requests":
        raise ValueError(f"{Path(out) / JUDGE_DIR / REQUESTS_NAME}: not an Objaverse judging requests file")
    for item in (doc or {}).get("items") or []:
        if not _SHA256_RE.match(str(item.get("input_sha256"))):
            raise ValueError(f"request {item.get('key')!r}: input_sha256 is not a sha256 hex digest")
    return doc


# Adapter over the recognition answer store (wenart/recognition/answers.py, owner Y): the file format, the model
# table (check.yaml), staleness and seeding are the same; only the task's schema and per-item prompt are ours.
# When answers.py learns per-item prompts and a task registry, ``judge`` can call ``answers.ask`` directly.
_STORE_CLASS = None


def _store_class():
    global _STORE_CLASS
    if _STORE_CLASS is None:
        from wenart.recognition.answers import AnswerStore

        class JudgeStore(AnswerStore):
            """``judge/answers_<slug>.json``: the recognition answer store with the library judging schema."""

            def valid(self, item: dict) -> Optional[dict]:
                rec = self.calls.get(item["key"])
                if not self.current(rec, item):
                    return None
                return rec if valid_judgement(rec.get("data"), item_kind(item)) else None

        _STORE_CLASS = JudgeStore
    return _STORE_CLASS


def judge_store(out: Path, key: str, models: Optional[dict] = None):
    from wenart.recognition import answers as A
    info = A.model_info(key, models)
    store = _store_class()(A.answers_path(Path(out) / JUDGE_DIR, info["slug"]), key, info["slug"], info["id"])
    store.data["kind"] = "objaverse_judge_answers"
    return store


def item_state(store, item: dict) -> str:
    rec = store.get(item["key"])
    if rec is None:
        return "missing"
    if not store.current(rec, item):
        return "stale"
    return "answered" if valid_judgement(rec.get("data"), item_kind(item)) else "failed"


def seed_store(store, items: list[dict], seed_dir: Path, log: Callable = print) -> int:
    """Copy current, schema-valid answers of ``<seed_dir>/answers_<slug>.json`` (same model id) into ``store``."""
    seed_path = Path(seed_dir) / f"answers_{store.data['slug']}.json"
    seed = read_json(seed_path)
    if seed is None:
        log(f"objaverse judge: no {seed_path.name} in {seed_dir}: nothing seeded")
        return 0
    if store.data["model"] and seed.get("model") and seed["model"] != store.data["model"]:
        log(f"objaverse judge: {seed_path} is from {seed['model']}, not {store.data['model']}: nothing seeded")
        return 0
    copied = 0
    for item in items:
        if store.valid(item) is not None:
            continue
        rec = (seed.get("calls") or {}).get(item["key"])
        if not store.current(rec, item) or not valid_judgement(rec.get("data"), item_kind(item)):
            continue
        store.put(item["key"], dict(rec, seeded_from=str(seed_path)), save=False)
        copied += 1
    if copied:
        store.save()
    return copied


def _spawn(fn: Callable, tag: int, results: "queue.Queue") -> None:
    """Run ``fn()`` in a daemon thread (a wedged call cannot keep the process alive) and queue its outcome."""
    def target():
        try:
            results.put((tag, fn(), None))
        except Exception as exc:  # noqa: BLE001 - recorded as a failed answer by the waiting thread
            results.put((tag, None, exc))

    threading.Thread(target=target, name=f"library-judge-{tag}", daemon=True).start()


def judge_ask(items: list[dict], store, client, out: Path, *, workers: int = 1, deadline: Optional[float] = None,
              seed: int = 0, log: Callable = print, clock: Callable[[], float] = time.time) -> dict:
    """Ask every item without a current answer, ``workers`` at once, until ``deadline`` (as
    ``wenart.recognition.answers.ask``: no call starts after it, none is waited for past it)."""
    judge_dir = Path(out) / JUDGE_DIR
    schemas = {k: judge_schema(k) for k in ("furniture", "decor")}
    stats = {"asked": 0, "reused": 0, "failed": 0, "left": 0, "incomplete": False}
    if deadline is not None and hasattr(client, "deadline"):
        client.deadline = float(deadline)
    model = str(getattr(client, "model", "") or store.data.get("model") or "")
    pending = []
    for item in items:
        if store.valid(item) is None:
            pending.append(item)
        else:
            stats["reused"] += 1
    results: "queue.Queue" = queue.Queue()
    running: dict[int, dict] = {}
    started = abandoned = 0
    while True:
        while started < len(pending) and len(running) < max(1, int(workers)):
            if deadline is not None and clock() >= deadline:
                break
            item = pending[started]
            running[started] = item

            def call(item=item):
                return client.run_schema([str(judge_dir / p) for p in item["images"]], item["prompt"],
                                         schemas[item_kind(item)], seed=seed, task=TASK, max_side=0, labels=None,
                                         system_prompt=SYSTEM_PROMPT)
            _spawn(call, started, results)
            started += 1
        if not running:
            break
        left = None if deadline is None else max(0.0, deadline - clock())
        try:
            tag, result, exc = results.get(timeout=left)
        except queue.Empty:
            abandoned = len(running)
            log(f"objaverse judge: deadline reached with {abandoned} call(s) unanswered")
            break
        item = running.pop(tag)
        rec = {"task": TASK, "input_sha256": item["input_sha256"], "model": model, "seed": seed,
               "images": list(item["images"])}
        if exc is not None:
            rec.update(data=None, raw_text="", error=f"{type(exc).__name__}: {exc}", attempts=0, latency_s=0.0)
        else:
            rec.update(data=result.data, raw_text=result.raw_text, error=result.error, attempts=result.attempts,
                       latency_s=round(float(result.latency_s), 3))
        store.put(item["key"], rec)
        stats["asked"] += 1
        if not valid_judgement(rec["data"], item_kind(item)):
            stats["failed"] += 1
            log(f"objaverse judge: {item['key']}: {rec['error'] or 'answer not schema-valid'}")
    stats["left"] = len(pending) - started + abandoned
    stats["incomplete"] = stats["left"] > 0
    store.data["incomplete"] = stats["incomplete"]
    if model:
        store.data["model"] = model
    store.save()
    return stats


def judge(out: Path, model_key: str, server: str = DEFAULT_SERVER, workers: Optional[int] = None,
          deadline: Optional[float] = None, seed_dir: Optional[Path] = None, client_factory=None,
          retries: int = 3, timeout_s: float = 600.0, log: Callable = print) -> int:
    """The ``judge`` command: seed, then ask the server for the rest. Exit 0 all answered, 3 deadline, 2 server
    or answer failure (as ``python -m wenart.recognition.answers ask``)."""
    from wenart.recognition import answers as A
    doc = read_requests(out)
    if doc is None:
        raise UsageError(f"{Path(out) / JUDGE_DIR / REQUESTS_NAME} not found: run judge-requests first")
    models = A.load_models()
    info = A.model_info(model_key, models)
    items = doc.get("items") or []
    store = judge_store(out, model_key, models)
    if seed_dir:
        n = seed_store(store, items, Path(seed_dir), log)
        log(f"objaverse judge [{model_key}]: {n} answer(s) seeded from {seed_dir}")
    pending = [i for i in items if store.valid(i) is None]
    if not pending:
        store.data["incomplete"] = False
        store.save()
        log(f"objaverse judge [{model_key}]: all {len(items)} item(s) answered -> {store.path}")
        return EXIT_OK
    deadline = deadline_of(deadline)
    if deadline is not None and time.time() >= deadline:
        store.data["incomplete"] = True
        store.save()
        log(f"objaverse judge [{model_key}]: deadline already passed, {len(pending)} item(s) left")
        return EXIT_DEADLINE
    if client_factory is None:
        from wenart.recognition import vlm_client
        if not vlm_client.health(server):
            log(f"objaverse judge [{model_key}]: no vLLM server answers at {server}")
            return EXIT_SERVER
        client = vlm_client.VLMClient(server, model=info["id"], retries=retries, timeout_s=timeout_s)
    else:
        client = client_factory(info, server)
    stats = judge_ask(items, store, client, out, workers=workers or _workers_default(), deadline=deadline, log=log)
    log(f"objaverse judge [{model_key}]: {len(items)} item(s): {stats['asked']} asked ({stats['failed']} failed), "
        f"{stats['reused']} reused, {stats['left']} left -> {store.path}")
    if stats["left"]:
        return EXIT_DEADLINE
    if any(store.valid(i) is None for i in items):
        return EXIT_SERVER
    return EXIT_OK


def _workers_default() -> int:
    try:
        import yaml
        from wenart.recognition.answers import CHECK_YAML
        cfg = yaml.safe_load(Path(CHECK_YAML).read_text(encoding="utf-8")) or {}
        return int((cfg.get("calls") or {}).get("workers", 1))
    except (OSError, ValueError, TypeError, ImportError):
        return 1


def judge_status(out: Path, models: Optional[dict] = None) -> dict:
    """``{"items", "complete", "models": {key: {slug, answered, stale, failed, missing, incomplete}}}``."""
    from wenart.recognition import answers as A
    doc = read_requests(out)
    if doc is None:
        raise UsageError(f"{Path(out) / JUDGE_DIR / REQUESTS_NAME} not found")
    items = doc.get("items") or []
    models = A.load_models() if models is None else models
    result = {"items": len(items), "models": {}}
    for key in MODEL_KEYS:
        store = judge_store(out, key, models)
        counts = {"answered": 0, "stale": 0, "failed": 0, "missing": 0}
        for item in items:
            counts[item_state(store, item)] += 1
        result["models"][key] = {"slug": store.data["slug"], **counts, "incomplete": bool(store.data["incomplete"])}
    result["complete"] = all(m["answered"] == len(items) for m in result["models"].values())
    return result


def load_judgements(out: Path, models: Optional[dict] = None) -> dict:
    """``{uid: {model_key: answer data | None}}`` for every request (current and schema-valid answers only)."""
    from wenart.recognition import answers as A
    doc = read_requests(out) or {"items": []}
    models = A.load_models() if models is None else models
    stores = {k: judge_store(out, k, models) for k in MODEL_KEYS if k in models}
    result: dict[str, dict] = {}
    for item in doc["items"]:
        uid = item["context"]["uid"]
        result[uid] = {}
        for key in MODEL_KEYS:
            rec = stores[key].valid(item) if key in stores else None
            result[uid][key] = clean_judgement(rec.get("data")) if rec else None
    return result


# --------------------------------------------------------------------------
# 5. Acceptance (§7.2)
# --------------------------------------------------------------------------

def deck_ok(obj: dict, cfg: dict) -> tuple[bool, str]:
    """Whether a bed's measured deck (``thumbnails``: ``deck``, ``deck_height_m``) makes it a usable bed frame
    (objaverse.yaml ``bed_frame``: at least ``min_hits`` of the 5 rays hit, the median inside ``deck_range_m``)."""
    bf = cfg.get("bed_frame") or {}
    lo, hi = (float(v) for v in bf.get("deck_range_m", (0.08, 0.90)))
    need = int(bf.get("min_hits", 3))
    deck = obj.get("deck") or {}
    hits = int(deck.get("hits") or 0)
    height = obj.get("deck_height_m")
    total = len(deck.get("hits_raw") or []) or 5
    if height is None or hits < need:
        return False, f"{hits} of {total} downward rays hit the frame (at least {need} needed)"
    if not lo <= float(height) <= hi:
        return False, f"deck {float(height):.3f} m above the floor is outside {lo:g}-{hi:g} m"
    return True, f"deck {float(height):.3f} m above the floor (median of {hits} of {total} downward rays)"


def decide(obj: dict, answers: dict, cfg: dict) -> dict:
    """Accept or refuse one ``ready`` object of ``thumbnails.json`` on both judges' answers.

    Returns ``{"uid", "type", "source", "kind", "decor_type", "accepted": bool, "code", "detail", "failed": [(code,
    detail), ...]}`` plus, when accepted, ``front_axis``, ``front_view``, ``front_axis_confidence``,
    ``front_axis_note``, ``styles``, ``style_note``, ``has_mattress``, ``bed_frame``, ``deck_height_m``, ``quality``,
    ``licence_flag``. Every failed rule is listed; ``code`` is the first.

    Milestone 8: decor answers ``is_decor_type``; a bed both judges see without a mattress is a bed frame when its
    deck was measured (``deck_ok``), else ``no_deck``; judges that disagree on the mattress -> ``mattress_not_agreed``;
    a documented front (ABO) replaces the geometric one: both judges naming another view refuse the object, judges
    that do not agree leave the documented front (source evidence decides, CLAUDE.md trust order)."""
    ftype = obj["type"]
    kind = obj.get("kind") or "furniture"
    out = {"uid": obj["uid"], "type": ftype, "source": obj.get("source") or SOURCE, "kind": kind,
           "decor_type": obj.get("decor_type") if kind == "decor" else None, "accepted": False, "failed": []}
    fail = out["failed"]
    a, b = (clean_judgement(answers.get(k)) for k in MODEL_KEYS)
    missing = [k for k in MODEL_KEYS if answers.get(k) is None]
    if missing:
        fail.append(("not_judged", ", ".join(missing)))
        out.update(code=fail[0][0], detail=fail[0][1])
        return out

    def both(name: str) -> str:
        return f"{MODEL_KEYS[0]} {a.get(name)!r}, {MODEL_KEYS[1]} {b.get(name)!r}"
    if not (a["is_single_object"] is True and b["is_single_object"] is True):
        fail.append(("not_single", both("is_single_object")))
    if kind == "decor":
        if not (a.get("is_decor_type") is True and b.get("is_decor_type") is True):
            fail.append(("not_decor_type", both("is_decor_type")))
    elif not (a.get("matches_type") is True and b.get("matches_type") is True):
        fail.append(("type_mismatch", both("matches_type")))
    min_q = int(cfg["accept"]["min_quality"])
    if min(int(a["photoreal_quality"]), int(b["photoreal_quality"])) < min_q:
        fail.append(("quality", both("photoreal_quality")))
    mattress, frame, deck_note = None, None, ""
    if kind != "decor" and ftype in BED_TYPES:
        ma, mb = a.get("has_mattress"), b.get("has_mattress")
        if ma is True and mb is True:
            mattress, frame = True, False
        elif ma is False and mb is False:
            ok, deck_note = deck_ok(obj, cfg)
            if ok:
                mattress, frame = False, True
            else:
                fail.append(("no_deck", f"both judges: no mattress; {deck_note}"))
        else:
            fail.append(("mattress_not_agreed", both("has_mattress")))
    if not (obj.get("unit") or {}).get("ok"):
        fail.append(("size_range", "no unit guess"))

    rule = cfg["types"][ftype]["front"]
    documented = obj.get("front_documented")
    if rule == FRONTLESS_RULE:
        front, view, confidence = "-Y", None, "low"
        front_note = f"{ftype} has no front: -Y kept as the model frame gives it (front_axis_confidence low)"
    elif documented:
        va, vb = a["front_view"], b["front_view"]
        doc_note = obj.get("front_documented_note") or "documented by the source"
        front, view, confidence, front_note = None, None, "high", ""
        if va is not None and va == vb and VIEW_SIDES[va] != documented:
            fail.append(("front_not_agreed", f"judges: view {va} ({VIEW_SIDES[va]}); documented front {documented} "
                                             f"({doc_note})"))
        elif va is not None and va == vb:
            front, view = documented, va
            front_note = (f"documented front {documented} ({doc_note}); both judges: view {va} (camera on the "
                          f"{VIEW_SIDES[va]} side) shows the front; geometry: {obj.get('geometric_note', '')}")
        else:
            front = documented
            front_note = (f"documented front {documented} ({doc_note}); the judges did not agree ({both('front_view')}): "
                          f"the documented front decides; geometry: {obj.get('geometric_note', '')}")
    else:
        va, vb = a["front_view"], b["front_view"]
        geo = obj.get("geometric_front")
        front, view, confidence = None, None, "high"
        generated = (obj.get("source") or SOURCE) == "generated"
        if va is None or vb is None or va != vb:
            fail.append(("front_not_agreed", f"judges: {both('front_view')}"))
        elif generated and geo != VIEW_SIDES[va]:
            # A generated model (TRELLIS.2) has no maker's detail on its back: the vertex-count rule reads the
            # generator's mesh, not a product's back (M8 pod L2: fridges and bathtubs "+Y" against both judges'
            # -Y). Both judges agreeing decide; the geometry is recorded.
            front, view = VIEW_SIDES[va], va
        elif geo is None:
            fail.append(("front_not_agreed", f"judges: view {va} ({VIEW_SIDES[va]}); geometry undecided "
                                             f"({obj.get('geometric_note', '')})"))
        elif VIEW_SIDES[va] != geo:
            fail.append(("front_not_agreed", f"judges: view {va} ({VIEW_SIDES[va]}); geometry {geo}"))
        else:
            front, view = geo, va
        front_note = (f"both judges: view {va} (camera on the {VIEW_SIDES[va]} side) shows the front; geometry: "
                      f"{obj.get('geometric_note', '')}" if front else "")
        if front and generated and geo != front:
            front_note += " (generated model: the judges decide; the geometry rule is for scanned products)"

    order = list(style_values())
    styles = [s for s in order if s in (a.get("styles") or []) and s in (b.get("styles") or [])]
    if not styles:
        fail.append(("no_common_style", both("styles")))
    if fail:
        out.update(code=fail[0][0], detail=fail[0][1])
        return out
    out.update({
        "accepted": True, "code": "", "detail": "", "front_axis": front, "front_view": view,
        "front_axis_confidence": confidence, "front_axis_note": front_note, "styles": styles,
        "style_note": (f"intersection of the two judges' styles on the 2 x 2 sheet: {MODEL_KEYS[0]} "
                       f"{a.get('styles')}, {MODEL_KEYS[1]} {b.get('styles')}"),
        "has_mattress": mattress, "bed_frame": frame,
        "deck_height_m": obj.get("deck_height_m") if frame else None, "deck_note": deck_note or None,
        "quality": [int(a["photoreal_quality"]), int(b["photoreal_quality"])],
        "licence_flag": obj.get("licence_flag"),
    })
    return out


def _rank_key(dec: dict, cand: dict, cfg: Optional[dict] = None) -> tuple:
    """Real models before generated ones, then mean quality, then the source order (abo, polyhaven, objaverse,
    generated), then the lower quality, likes, views, the survey rank and the uid (docs/milestone8.md §2)."""
    q = dec["quality"]
    order = list(((cfg or {}).get("accept") or {}).get("source_order") or SOURCE_ORDER)
    source = dec.get("source") or SOURCE
    # Generated models fill gaps only (docs/milestone8.md §1): they rank after every real model, so the type and
    # style limits never drop a real product for a generated one (M8 pod L2: two Japandi sofas did).
    return (source == "generated", -sum(q) / len(q), order.index(source) if source in order else len(order), -min(q),
            -(cand.get("likes") or 0), -(cand.get("views") or 0), cand.get("rank") or 0, dec["uid"])


def accept(out: Path, cfg: Optional[dict] = None, models: Optional[dict] = None, sources=None) -> dict:
    """Decide every ``ready`` object (of ``sources`` only, when given), keep <= ``per_type_max`` per furniture type
    (``decor_per_type_max`` per decor type) and <= ``per_family_max`` per (type, style family) -> ``accepted.json``.

    In rank order (``_rank_key``) a model is kept while its type has room and one of its style families (``neutral``
    counts as one) has fewer than ``per_family_max`` kept models; it then counts for each of its families. Refused:
    ``over_type_limit``, ``over_style_limit``. Milestone 9 (``style_fill``, docs/milestone9.md §1): a fill pass then
    keeps the models refused for their style, in rank order, until the type limit (``style_fill: true`` and a note in
    the decision); the ones left are ``over_type_limit``.

    ``accepted.json`` (also the ``--catalog`` of ``wenart.assets.generate plan``, docs/milestone8.md §3, after the
    prep job's first accept with ``sources=["abo", "objaverse"]``): ``{"kind": "objaverse_accepted", "sources":
    "all" | [...], "limits", "counts", "accepted_by_source", "accepted": [decision], "refused": [decision]}``; a
    decision (``decide``) has ``uid``, ``type`` (the furniture or decor type), ``source``, ``kind``, ``decor_type``,
    ``styles`` (families or ``neutral``), ``quality``, ``front_axis``, ``has_mattress``, ``bed_frame``,
    ``deck_height_m``, ``licence_flag`` (refused ones ``code`` and ``detail`` instead)."""
    cfg = cfg or load_config()
    out = Path(out)
    thumbs = read_json(out / THUMBS_JSON)
    if thumbs is None:
        raise UsageError("thumbnails.json missing: run the survey(s) and thumbnails first")
    cands = {c["uid"]: c for c in load_candidates(out)}
    wanted = None if sources is None else set(sources)
    answers = load_judgements(out, models)
    decisions = []
    for uid, obj in sorted(thumbs["objects"].items()):
        if obj.get("status") != "ready":
            continue
        if wanted is not None and (obj.get("source") or SOURCE) not in wanted:
            continue
        decisions.append(decide(obj, answers.get(uid) or {}, cfg))
    acc_cfg = cfg["accept"]
    per_family = int(acc_cfg.get("per_family_max", 3))
    style_fill = bool(acc_cfg.get("style_fill", False))
    accepted, refused = [], []
    groups: dict[tuple, list[dict]] = {}
    for dec in decisions:
        if dec["accepted"]:
            groups.setdefault((dec["kind"], dec["type"]), []).append(dec)
        else:
            refused.append(dec)
    for kind, ftype in sorted(groups):
        limit = int(acc_cfg["decor_per_type_max"] if kind == "decor" else acc_cfg["per_type_max"])
        ranked = sorted(groups[(kind, ftype)], key=lambda d: _rank_key(d, cands.get(d["uid"], {}), cfg))
        kept, families, left = [], {}, []
        for n, dec in enumerate(ranked):
            full = [f for f in dec["styles"] if families.get(f, 0) >= per_family]
            if len(kept) >= limit:
                refused.append(dict(dec, accepted=False, code="over_type_limit",
                                    detail=f"rank {n + 1} of {len(ranked)} accepted {ftype} models (keep {limit})",
                                    failed=[("over_type_limit", f"keep {limit}")]))
            elif len(full) == len(dec["styles"]):
                left.append((n, dec, full))
            else:
                kept.append((n, dec))
                for f in dec["styles"]:
                    families[f] = families.get(f, 0) + 1
        # Milestone 9 (docs/milestone9.md §1): the first pass spreads the styles; the fill pass then takes the models
        # it left for their style, in rank order, until the type limit.
        for n, dec, full in left:
            if style_fill and len(kept) < limit:
                kept.append((n, dict(dec, style_fill=True,
                                     style_note=dec.get("style_note", "") + f"; kept by the fill pass ({ftype} had "
                                     f"{per_family} models of each of its styles: {', '.join(full)})")))
            elif style_fill:
                refused.append(dict(dec, accepted=False, code="over_type_limit",
                                    detail=f"rank {n + 1} of {len(ranked)} accepted {ftype} models (keep {limit}; "
                                           f"its styles {', '.join(full)} had {per_family} each in the first pass)",
                                    failed=[("over_type_limit", f"keep {limit}")]))
            else:
                refused.append(dict(dec, accepted=False, code="over_style_limit",
                                    detail=f"rank {n + 1}: {ftype} already has {per_family} models of each of its "
                                           f"styles ({', '.join(full)})",
                                    failed=[("over_style_limit", f"keep {per_family} per family")]))
        accepted += [dec for _n, dec in sorted(kept, key=lambda item: item[0])]
    counts: dict[str, int] = {"accepted": len(accepted)}
    for dec in refused:
        counts[dec["code"]] = counts.get(dec["code"], 0) + 1
    by_source: dict[str, int] = {}
    for dec in accepted:
        by_source[dec["source"]] = by_source.get(dec["source"], 0) + 1
    doc = {"schema_version": SCHEMA_VERSION, "kind": "objaverse_accepted", "generated_utc": now_utc(),
           "rules": "docs/milestone7.md §7.2, docs/milestone8.md §2",
           "sources": sorted(wanted) if wanted is not None else "all",
           "limits": {"per_type_max": int(acc_cfg["per_type_max"]),
                      "decor_per_type_max": int(acc_cfg["decor_per_type_max"]), "per_family_max": per_family,
                      "style_fill": style_fill},
           "counts": counts, "accepted_by_source": dict(sorted(by_source.items())), "accepted": accepted,
           "refused": sorted(refused, key=lambda d: d["uid"])}
    write_json(out / ACCEPTED_NAME, doc)
    return doc


# --------------------------------------------------------------------------
# 6. Catalogue (wenart/furniture/catalog.py frame fields, §6.6 fields, §7.3 credits)
# --------------------------------------------------------------------------

GENERATED_AUTHOR = "generated (TRELLIS.2-4B)"
GENERATED_FIELDS = ("prompt", "image_sha256", "model", "revision", "seed")      # = catalog.GENERATED_FIELDS


def entry_id(source: str, uid: str) -> str:
    """The catalogue id of a library model: ``objaverse_<uid>`` (M7) for Objaverse, the uid itself for the sources
    whose uid carries its own prefix (``abo_<3dmodel_id>``, ``gen_<type>_<family>_<n>_<sha8>``)."""
    return f"{ID_PREFIX}{uid}" if source == SOURCE else str(uid)


def cache_rel(source: str, uid: str) -> str:
    """``models/<source>/<uid>.glb`` (relative to the assets dir; ``wenart.assets.models.library_relpath``)."""
    return f"models/{source}/{uid}.glb"


def generated_record(cand: dict) -> dict:
    """The ``generated`` record of a generated candidate: its own ``generated`` dict, completed from the record's
    top-level fields of the same names (docs/milestone8.md §2: prompt, image hash, model, revision, seed)."""
    rec = dict(cand.get("generated") or {})
    for key in GENERATED_FIELDS:
        rec.setdefault(key, cand.get(key))
    return rec


def catalog_entry(cand: dict, obj: dict, dec: dict, sha: str, cfg: dict, answers: Optional[dict] = None) -> dict:
    """One ``catalog_library.json`` entry. Boxes are metres in the model frame of the glTF importer (Z up): the
    measured raw box times ``unit_scale``; the scene builder must scale the imported mesh by ``unit_scale`` before
    the fit (``fit_scale`` maps metres to the footprint). Decor models get the type ``decor_<decor_type>`` (they go
    to the catalogue's ``decor`` section)."""
    from wenart.furniture import catalog as C
    u = float(obj["unit"]["scale"])
    m = obj["measure"]
    mn = [round(float(v) * u, 4) for v in m["bbox_min_raw"]]
    mx = [round(float(v) * u, 4) for v in m["bbox_max_raw"]]
    model = [round((float(m["bbox_max_raw"][i]) - float(m["bbox_min_raw"][i])) * u, 4) for i in range(3)]
    front = dec["front_axis"]
    uid, source = cand["uid"], cand["source"]
    kind = dec.get("kind") or "furniture"
    title = cand.get("title") or (f"generated {dec['type']}" if source == "generated" else uid)
    entry = {
        "id": entry_id(source, uid), "type": f"decor_{dec['decor_type']}" if kind == "decor" else dec["type"],
        "source": source, "licence": cand["licence"], "licence_flag": cand.get("licence_flag"),
        "licence_url": cand.get("licence_url") or licence_url(cand["licence"], cfg), "name": title,
        "bbox_m": C.oriented_bbox(model, front), "bbox_model_m": model, "bbox_min_m": mn, "bbox_max_m": mx,
        "front_axis": front, "up_axis": "+Z", "origin_offset": C.origin_offset(mn, mx),
        "front_axis_confidence": dec["front_axis_confidence"], "front_axis_note": dec["front_axis_note"],
        "unit_scale": u, "unit_note": obj["unit"]["note"], "units_known": bool(cand.get("units_known")),
        "styles": list(dec["styles"]), "style_note": dec["style_note"], "kind": kind,
        "glb": cache_rel(source, uid), "sha256_glb": sha, "uid": uid,
        "title": title, "author": cand.get("author") or (GENERATED_AUTHOR if source == "generated" else ""),
        "source_url": cand.get("source_url") or "", "via": cand.get("via") or cfg["attribution"]["via"],
        "attribution": credit_line(cand, cfg),
        "polycount": m.get("triangles"), "vertices": m.get("vertices"),
        "textured": bool((cand.get("glb_info") or {}).get("textured")),
        "vertex_colours": bool((cand.get("glb_info") or {}).get("vertex_colours")),
        "quality": list(dec["quality"]), "judged": answers or {}, "thumbnail": obj.get("thumb"),
    }
    if kind == "decor":
        entry["decor_type"] = dec["decor_type"]
    else:
        entry["has_mattress"] = dec.get("has_mattress")
        if dec["type"] in BED_TYPES:
            entry["bed_frame"] = bool(dec.get("bed_frame"))
            if dec.get("bed_frame"):
                entry["deck_height_m"] = dec["deck_height_m"]
                entry["deck_note"] = dec.get("deck_note")
    if source == SOURCE:
        entry.update({"lvis_categories": list(cand.get("categories") or []),
                      "objaverse_path": cand.get("object_path"), "dataset_revision": cfg["dataset"]["revision"],
                      "likes": cand.get("likes"), "views": cand.get("views")})
    elif source == "abo":
        entry.update({"abo_item_id": cand.get("item_id"), "abo_3dmodel_id": cand.get("abo_3dmodel_id"),
                      "abo_path": cand.get("object_path"), "abo_product_type": cand.get("product_type"),
                      "brand": cand.get("brand"), "style_hint": cand.get("style_hint")})
    elif source == "generated":
        entry.update({"generated": generated_record(cand), "style_hint": cand.get("style_hint")})
    return entry


def copy_glb(src: Path, assets: Path, uid: str, sha: str, source: str = SOURCE) -> Path:
    """``<assets>/models/<source>/<uid>.glb`` with sha256 ``sha`` (copied when missing or different)."""
    dst = Path(assets) / cache_rel(source, uid)
    if dst.is_file() and sha256_file(dst) == sha:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_name(dst.name + ".part")
    shutil.copyfile(Path(src), tmp)
    got = sha256_file(tmp)
    if got != sha:
        tmp.unlink()
        raise ValueError(f"{uid}: copied GLB has sha256 {got[:12]}..., expected {sha[:12]}...")
    tmp.replace(dst)
    return dst


def glb_source(cand: dict, assets: Path) -> Optional[Path]:
    """The GLB file of an accepted candidate with the survey's sha256: the survey's own path (the source's cache on
    the container disk), else the copy an earlier ``write-catalog`` put into the assets cache on the volume (a later
    pod that did not survey again); None when neither holds it."""
    sha = cand.get("glb_sha256")
    for path in (cand.get("glb"), Path(assets) / cache_rel(cand["source"], cand["uid"])):
        if path and Path(path).is_file() and sha256_file(Path(path)) == sha:
            return Path(path)
    return None


DATASETS = {
    "objaverse": lambda cfg: {k: cfg["dataset"][k] for k in ("repo", "revision", "licence", "licence_url", "page")},
}


def _dataset_info(source: str, cfg: dict) -> dict:
    if source == SOURCE:
        return DATASETS[SOURCE](cfg)
    if source == "abo":
        from wenart.assets import abo
        ds = abo.load_config()["dataset"]
        return {k: ds[k] for k in ("name", "index_url", "licence", "licence_url", "credit_data", "credit_dataset")}
    return {"name": "generated (TRELLIS.2-4B)", "licence": "MIT (model); output marked generated"}


def write_catalog(out: Path, assets: Path, cfg: Optional[dict] = None, base_catalog: Optional[Path] = None,
                  models: Optional[dict] = None, log: Callable = print) -> Optional[dict]:
    """``catalog_library.json`` from ``accepted.json`` (None and no file when nothing is accepted; a stale file in
    ``out`` is removed). Every GLB is copied to ``<assets>/models/<source>/<uid>.glb`` with its sha256 checked
    against the survey (``glb_source``); furniture goes to ``entries``, decor to ``decor``; the result must pass
    ``catalog.validate(complete=False)`` and merge with ``catalog.json``."""
    from wenart.furniture import catalog as C
    cfg = cfg or load_config()
    out = Path(out)
    acc, thumbs = (read_json(out / n) for n in (ACCEPTED_NAME, THUMBS_JSON))
    if acc is None or thumbs is None:
        raise UsageError("accepted.json / thumbnails.json missing: run accept first")
    cands = {c["uid"]: c for c in load_candidates(out)}
    answers = load_judgements(out, models)
    entries, decor, problems = [], [], []
    for dec in acc["accepted"]:
        uid = dec["uid"]
        cand, obj = cands[uid], thumbs["objects"][uid]
        src = glb_source(cand, assets)
        if src is None:
            problems.append({"uid": uid, "code": "glb_changed", "detail": str(cand.get("glb"))})
            continue
        copy_glb(src, assets, uid, cand["glb_sha256"], cand["source"])
        entry = catalog_entry(cand, obj, dec, cand["glb_sha256"], cfg, answers.get(uid))
        (decor if entry["kind"] == "decor" else entries).append(entry)
    path = out / CATALOG_NAME
    if not entries and not decor:
        if path.exists():
            path.unlink()
        log(f"library write-catalog: no accepted model: {CATALOG_NAME} not written")
        return None
    entries.sort(key=lambda e: (C.FURNITURE_TYPES.index(e["type"]), e["id"]))
    decor.sort(key=lambda e: (DECOR_TYPES.index(e["decor_type"]), e["id"]))
    sources = sorted({e["source"] for e in entries + decor}, key=SOURCE_ORDER.index)
    notices = source_notices(sources, cfg)
    licences: dict[str, int] = {}
    flags: dict[str, int] = {}
    for e in entries + decor:
        licences[e["licence"]] = licences.get(e["licence"], 0) + 1
        if e.get("licence_flag"):
            flags[e["licence_flag"]] = flags.get(e["licence_flag"], 0) + 1
    file_licences = (["ODC-By-1.0"] if SOURCE in sources else []) + (["CC-BY-4.0"] if "abo" in sources else [])
    doc = {
        "schema_version": SCHEMA_VERSION, "kind": "library_catalog", "sources": sources,
        "generated_utc": now_utc(), "file_licence": file_licences[0] if file_licences else "MIT",
        "file_licences": file_licences, "notice": "\n\n".join(notices), "notices": notices,
        "datasets": {s: _dataset_info(s, cfg) for s in sources},
        "licences_verified": bool(cfg["licences"].get("verified")),
        "counts": {"entries": len(entries), "decor": len(decor),
                   "by_source": {s: sum(1 for e in entries + decor if e["source"] == s) for s in sources},
                   "licences": dict(sorted(licences.items())), "licence_flags": dict(sorted(flags.items())),
                   "bed_frames": sum(1 for e in entries if e.get("bed_frame"))},
        "notes": [
            "Written by python -m wenart.assets.objaverse write-catalog on the prep pod (docs/milestone8.md §2); the "
            "integrator copies it into wenart/furniture/ before the full runs (catalog.load merges it, else the M7 "
            "catalog_objaverse.json).",
            "Boxes are metres in the Z-up frame of Blender's glTF importer: the raw GLB box times unit_scale (the "
            "unit guess; 1 for sources with known units: ABO). The scene builder scales the imported mesh by "
            "unit_scale before fit_scale.",
            "front_axis: the side both judges named on the 2 x 2 sheet, equal to the geometric check, or the "
            "source's documented front (ABO: glTF +Z = -Y) that no judge pair contradicts (front_axis_note); "
            "front-less types keep -Y with front_axis_confidence low.",
            "styles: the intersection of both judges' answers (neutral only when both name it). Beds: has_mattress "
            "from both judges; bed_frame true = no mattress, a deck at deck_height_m (the builder adds the bedding).",
            "Licences: every licence is recorded; licence_flag marks the ones that are not CC0 / CC BY 4.0 "
            "(non_commercial, share_alike, no_derivatives, unknown). Objaverse licences are uploader-declared and "
            "unverified: check them before commercial use.",
        ],
        "refused_at_write": problems,
        "entries": entries,
        "decor": decor,
    }
    if SOURCE in sources:
        doc["dataset"] = _dataset_info(SOURCE, cfg)
    C.validate(doc, complete=False)
    base = read_json(base_catalog or C.CATALOG_PATH)
    C.Catalog(C.merge(base, doc))                         # must merge with the Poly Haven catalogue
    write_json(path, doc)
    log(f"library write-catalog: {len(entries)} model(s) and {len(decor)} decor model(s) -> {path}; GLBs in "
        f"{Path(assets) / 'models'}/<source>/")
    return doc


# --------------------------------------------------------------------------
# 7. Report
# --------------------------------------------------------------------------

def _table(header: list[str], rows: list[list]) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]
    return lines


def _count(items, key) -> dict:
    out: dict = {}
    for item in items:
        k = key(item)
        out[k] = out.get(k, 0) + 1
    return out


def _by_source(items) -> str:
    counts = _count(items, lambda d: d.get("source") or SOURCE)
    return ", ".join(f"{s} {n}" for s, n in sorted(counts.items(), key=lambda kv: SOURCE_ORDER.index(kv[0])
                                                    if kv[0] in SOURCE_ORDER else 99))


def library_types(cfg: dict) -> list[str]:
    """The furniture types a library source can fill: the Objaverse categories' and the ABO rules' (beds both)."""
    from wenart.furniture import catalog as C
    types = {t for spec in cfg["categories"].values() for t in spec["types"]}
    try:
        from wenart.assets import abo
        for rule in abo.load_config()["rules"]:
            for t in rule["types"]:
                types.update(BED_TYPES if t == "bed" else [t])
    except (OSError, ImportError, KeyError):
        pass
    return sorted((t for t in types if t in C.FURNITURE_TYPES), key=C.FURNITURE_TYPES.index)


def report(out: Path, cfg: Optional[dict] = None, models: Optional[dict] = None,
           base_catalog: Optional[Path] = None) -> str:
    """``library_report.md`` from whatever steps have run (missing files are reported as not run): every source
    (counts, licences and flags, credits), the refusals by reason, the style coverage (the Poly Haven models of
    ``base_catalog``, default ``catalog.json``, count too), bed frames, the catalogue and the attribution list."""
    from wenart.furniture import catalog as C
    cfg = cfg or load_config()
    out = Path(out)
    surveys = load_surveys(out)
    thumbs = read_json(out / THUMBS_JSON)
    acc = read_json(out / ACCEPTED_NAME)
    cat = read_json(out / CATALOG_NAME)
    sources_seen = [s for s in SOURCE_ORDER if s in surveys]
    ds = cfg["dataset"]
    lines = ["# Furniture library (docs/milestone7.md §7, docs/milestone8.md §2)", ""]
    for text in source_notices(sources_seen or [SOURCE], cfg):
        lines += [text, ""]
    lines += [f"Objaverse: [{ds['repo']}]({ds['page']}) @ `{ds['revision'][:7]}` ({ds['licence']}). Licence strings "
              f"and metadata field names of objaverse.yaml verified on the pod: "
              f"{'yes' if cfg['licences'].get('verified') else 'no (to verify: see Licence values seen)'}. Every "
              "licence is taken (docs/milestone8.md §2); not CC0 / CC BY 4.0 -> licence_flag.", ""]
    if not surveys:
        lines += ["Survey not run.", ""]
        text = "\n".join(lines) + "\n"
        (out / REPORT_NAME).write_text(text, encoding="utf-8")
        return text
    cands = load_candidates(out)
    objects = (thumbs or {}).get("objects") or {}
    judged = {}
    try:
        if read_requests(out) is not None:
            judged = load_judgements(out, models)
    except (OSError, ValueError, KeyError):
        judged = {}
    both_ok = {u for u, v in judged.items() if all(v.get(k) is not None for k in MODEL_KEYS)}
    entries = ((cat or {}).get("entries") or []) + ((cat or {}).get("decor") or [])
    accepted = (acc or {}).get("accepted") or []

    lines += ["## Sources", ""]
    rows = []
    for s in sources_seen:
        sc = [c for c in cands if c["source"] == s]
        so = [o for o in objects.values() if (o.get("source") or SOURCE) == s]
        rows.append([s, SURVEY_FILES[s], len(sc), sum(1 for c in sc if c.get("glb")),
                     sum(1 for o in so if o.get("status") == "ready") if thumbs else "not run",
                     sum(1 for o in so if o["uid"] in both_ok) if judged else "not run",
                     sum(1 for d in accepted if d.get("source") == s) if acc else "not run",
                     sum(1 for e in entries if e.get("source") == s) if cat else "not written"])
    lines += _table(["Source", "Survey file", "Candidates", "With GLB", "Ready", "Judged by both", "Accepted",
                     "In catalogue"], rows)

    counts = (surveys.get(SOURCE) or {}).get("counts") or {}
    ready = sum(1 for o in objects.values() if o.get("status") == "ready")
    normalised = sum(1 for o in objects.values()
                     if o.get("status") == "ready" and (o.get("unit") or {}).get("normalised"))
    rendered = sum(1 for o in objects.values() if "measure" in o)
    lines += ["", "## Steps", ""]
    lines += _table(["Step", "Objects"], [
        ["Objaverse: LVIS objects in the mapped categories", sum(c.get("lvis", 0) for c in counts.values())],
        ["Objaverse: licence CC0 or CC BY 4.0 (metadata)", sum(c.get("licence_ok", 0) for c in counts.values())],
        ["Objaverse: other licences (taken, flagged)", sum(c.get("flagged", 0) for c in counts.values())],
        ["Objaverse: past the metadata prefilter (credit, faces, size)",
         sum(c.get("prefilter_ok", 0) for c in counts.values())],
        ["Candidates of every source (downloaded; textured or vertex-coloured)", sum(1 for c in cands if c.get("glb"))],
        ["Rendered (thumbnails)", rendered if thumbs else "not run"],
        ["Ready for judging (unit and type resolved)", ready if thumbs else "not run"],
        [f"of which {NORMALISED_NOTE}", normalised if thumbs else "not run"],
        ["Judged by both models", len(both_ok) if judged else "not run"],
        ["Accepted", len(accepted) if acc else "not run"],
        [f"In {CATALOG_NAME}", len(entries) if cat else "not written"],
    ])

    per_type: dict[tuple, dict] = {}
    for c in cands:
        d = per_type.setdefault((c["group"], c["source"]), {"cand": 0, "ready": 0, "accepted": 0, "catalog": 0})
        d["cand"] += 1
    for o in objects.values():
        if o.get("status") == "ready":
            per_type.setdefault((o["type"], o.get("source") or SOURCE),
                                {"cand": 0, "ready": 0, "accepted": 0, "catalog": 0})["ready"] += 1
    for dec in accepted:
        per_type.setdefault((dec["type"], dec.get("source") or SOURCE),
                            {"cand": 0, "ready": 0, "accepted": 0, "catalog": 0})["accepted"] += 1
    for e in entries:
        t = e.get("decor_type") or e["type"]
        per_type.setdefault((t, e["source"]), {"cand": 0, "ready": 0, "accepted": 0, "catalog": 0})["catalog"] += 1
    type_rows = []
    for (group, source), d in sorted(per_type.items(), key=lambda kv: (kv[0][0], SOURCE_ORDER.index(kv[0][1])
                                                                        if kv[0][1] in SOURCE_ORDER else 99)):
        lvis = counts.get(group, {}).get("lvis", "–") if source == SOURCE else "–"
        type_rows.append([group, source, lvis, d["cand"], d["ready"], d["accepted"], d["catalog"]])
    lines += ["", "## Per type (Objaverse bed candidates are split into bed_single / bed_double after the unit "
                  "guess)", ""]
    lines += _table(["Type", "Source", "LVIS", "Candidates", "Ready", "Accepted", "In catalogue"], type_rows)

    refusal_rows = []
    survey_refused = [r for s, doc in surveys.items() for r in (doc.get("refused") or [])
                      for r in [dict(r, source=r.get("source") or s)]]
    for code, items in sorted(_count(survey_refused, lambda r: r["code"]).items()):
        rs = [r for r in survey_refused if r["code"] == code]
        refusal_rows.append(["survey", code, REASONS.get(code, code), items, _by_source(rs)])
    nsel = sum(c.get("not_selected", 0) for doc in surveys.values() for c in (doc.get("counts") or {}).values()
               if isinstance(c, dict))
    if nsel:
        refusal_rows.append(["survey", "not_selected", "below the candidates per type (rank, or the pick order)",
                             nsel, ""])
    th_refused = [o for o in objects.values() if o.get("status") != "ready"]
    for code, n in sorted(_count(th_refused, lambda o: o["code"]).items()):
        refusal_rows.append(["thumbnails", code, REASONS.get(code, code), n,
                             _by_source([o for o in th_refused if o["code"] == code])])
    acc_refused = (acc or {}).get("refused") or []
    for code, n in sorted(_count(acc_refused, lambda d: d["code"]).items()):
        refusal_rows.append(["accept", code, REASONS.get(code, code), n,
                             _by_source([d for d in acc_refused if d["code"] == code])])
    lines += ["", "## Refusals by reason (first failed rule per object)", ""]
    lines += _table(["Step", "Code", "Reason", "Objects", "Sources"], refusal_rows or [["–", "–", "none", 0, ""]])

    surv = surveys.get(SOURCE)
    if surv is not None:
        lic_rows = []
        for value, n in (surv.get("licence_values") or {}).items():
            name, flag, _ = classify_licence(value if value != "(none)" else None, cfg)
            lic_rows.append([f"`{value}`", n, name, flag or "–"])
        lines += ["", "## Licence values seen (Objaverse metadata field `" + str(cfg["metadata_fields"]["licence"])
                  + "`)", ""]
        lines += _table(["Value", "Objects", "Licence", "Flag"], lic_rows or [["–", 0, "–", "–"]])
        lv = surv.get("lvis") or {"found": {}, "missing": []}
        lines += ["", "## LVIS categories", "",
                  "Found: " + (", ".join(f"`{c}` {n}" for c, n in sorted(lv["found"].items())) or "none") + ".",
                  "Missing (a warning: their types stay parametric): "
                  + (", ".join(f"`{c}`" for c in lv["missing"]) or "none") + ".", ""]
        for c, names in sorted((lv.get("near_missing") or {}).items()):
            lines += [f"- `{c}`: names in the file sharing a word: " + (", ".join(f"`{n}`" for n in names) or "none")
                      + " (an alternate needs a reason in objaverse.yaml)."]
        if lv.get("near_missing"):
            lines += [""]
        if surv.get("missing_fields"):
            lines += ["Metadata fields missing: " + ", ".join(f"{k} {v}" for k, v in surv["missing_fields"].items())
                      + ".", ""]
    abo_doc = surveys.get("abo")
    if abo_doc is not None:
        rows = [[t, c.get("mapped", 0), c.get("in_size", 0), c.get("candidates", 0), c.get("not_selected", 0)]
                for t, c in sorted((abo_doc.get("counts") or {}).items())]
        lines += ["", "## ABO mapping (abo.yaml rules; units known: metres)", ""]
        lines += _table(["Type", "Mapped", "In the size range", "Candidates", "Not selected"], rows or [["–"] * 5])
        unmapped = abo_doc.get("unmapped_product_types") or {}
        lines += ["", "Product types with a 3D model left unmapped: "
                  + (", ".join(f"{k} {v}" for k, v in list(unmapped.items())[:30]) or "none") + "."]

    lines += ["", "## Licence flags (catalogue)", ""]
    flag_rows = [[lic, C.licence_flag_of(lic) or "–", n] for lic, n in
                 sorted(_count(entries, lambda e: e["licence"]).items())]
    lines += _table(["Licence", "Flag", "Models"], flag_rows or [["–", "–", 0]])

    families = [s for s in style_values() if s != C.NEUTRAL]
    types = library_types(cfg)
    furniture = (cat or {}).get("entries") or []
    try:
        polyhaven = [e for e in C.load(base_catalog, objaverse=False).models if e.get("source") == "polyhaven"]
    except (OSError, ValueError):
        polyhaven = []
    cov_rows, gaps = [], []
    for t in types:
        row = [t]
        for fam in families:
            n_l = sum(1 for e in furniture if e["type"] == t and C.styles_match(e, fam) and C.bed_usable(e))
            n_p = sum(1 for e in polyhaven if e["type"] == t and C.styles_match(e, fam) and C.bed_usable(e))
            row.append(f"{n_l}+{n_p}" if n_l or n_p else "–")
            if not (n_l or n_p):
                gaps.append(f"{t}/{fam}")
        cov_rows.append(row)
    lines += ["", "## Style coverage", "",
              "Models per type and style family: library + Poly Haven (`neutral` counts for every family; beds with a "
              "mattress or as a bed frame with a deck). `–` = no model: refit builds the parametric mesh for that "
              "pair (or a generated model fills it, docs/milestone8.md §3).", ""]
    lines += _table(["Type"] + families, cov_rows)
    lines += ["", f"Parametric: {len(gaps)} of {len(types) * len(families)} type/family pairs"
                  + (f" ({', '.join(gaps)})." if len(gaps) <= 40 else "."), ""]

    beds = [e for e in furniture if e["type"] in BED_TYPES]
    if beds:
        lines += ["## Beds", ""]
        lines += _table(["Id", "Type", "Source", "Mattress", "Bed frame", "Deck (m)"],
                        [[f"`{e['id']}`", e["type"], e["source"], e.get("has_mattress"), e.get("bed_frame", False),
                          e.get("deck_height_m") or "–"] for e in beds])
        lines += [""]

    lines += ["## Catalogue", ""]
    if entries:
        rows = []
        for e in entries:
            rows.append([e.get("decor_type") or e["type"], e["source"], f"`{e['id']}`", e.get("title"),
                         e.get("author"), e["licence"], e.get("licence_flag") or "–", ", ".join(e["styles"]),
                         f"{e['front_axis']} ({e['front_axis_confidence']})", "/".join(str(q) for q in e["quality"]),
                         _fmt_dims(e["bbox_m"]), f"x{e['unit_scale']:g}"])
        lines += _table(["Type", "Source", "Id", "Title", "Author", "Licence", "Flag", "Styles", "Front", "Quality",
                         "W x D x H (m)", "Unit"], rows)
    else:
        lines += ["No catalogue written."]
    lines += ["", "## Attribution", ""]
    for text in source_notices(sorted({e["source"] for e in entries}, key=SOURCE_ORDER.index) or [SOURCE], cfg):
        lines += [text, ""]
    lines += [f"- {e['attribution']}" + (f" (licence flag: {e['licence_flag']})" if e.get("licence_flag") else "")
              for e in entries] or ["- (no model in the catalogue)"]
    if acc and acc.get("refused"):
        lines += ["", "## Refused after judging", ""]
        lines += _table(["uid", "Source", "Type", "Reason"],
                        [[d["uid"], d.get("source") or SOURCE, d["type"], reason_text(d["code"], d.get("detail", ""))]
                         for d in acc["refused"]])
    text = "\n".join(lines) + "\n"
    (out / REPORT_NAME).write_text(text, encoding="utf-8")
    return text


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

class UsageError(ValueError):
    """A step run before its inputs exist, or a wrong argument: the CLI prints it and exits 2."""


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.assets.objaverse",
                                     description="the furniture library for the prep pod: the Objaverse survey and "
                                                 "the steps of every source (docs/milestone7.md §7, "
                                                 "docs/milestone8.md §2)")
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--out", required=True, help="library folder ($RESULTS/library)")
        p.add_argument("--config", default=None, help="objaverse.yaml (default: next to this module)")
        return p

    p = add("survey", "LVIS -> types, licences, prefilter, candidates (downloads)")
    p.add_argument("--cache", default=None, help="HF_HOME of the pod (/opt/wenart/hf); files go to <cache>/hub")
    p.add_argument("--mirror", default=None, help="read the dataset files from this folder instead of the hub")
    p.add_argument("--no-download", action="store_true", help="rank only; download no GLB")
    p.add_argument("--workers", type=int, default=8, help="parallel metadata downloads (default 8)")
    p = add("thumbnails", "measure and render the candidates in Blender; unit guess; 2 x 2 sheets")
    p.add_argument("--work", default=None, help="views and measurements (default <out>/work)")
    p.add_argument("--blender", default=None, help="Blender binary (default WENART_BLENDER, /workspace/tools/...)")
    p.add_argument("--device", default="auto", choices=["auto", "cpu"])
    p.add_argument("--deadline", type=float, default=None, help="epoch seconds (default env WENART_DEADLINE)")
    add("judge-requests", "write judge/requests.json")
    p = add("judge", "ask one model (inside its vLLM session)")
    p.add_argument("--model-key", required=True, help="qwen (pass 1) | glm (pass 2)")
    p.add_argument("--server", default=DEFAULT_SERVER)
    p.add_argument("--workers", type=int, default=None)
    p.add_argument("--deadline", type=float, default=None)
    p.add_argument("--seed-answers", default=None, help="folder with answers_<slug>.json to copy matching answers")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=float, default=600.0)
    p = add("judge-status", "answered / stale / failed / missing per model")
    p.add_argument("--json", action="store_true")
    p = add("accept", "apply the §7.2 rules (docs/milestone8.md §2) -> accepted.json")
    p.add_argument("--sources", default=None,
                   help=f"only these sources, comma separated (default: every one; {','.join(SOURCES)})")
    p = add("write-catalog", f"{CATALOG_NAME} and the GLB cache")
    p.add_argument("--assets", default="/workspace/assets", help="assets dir (GLBs to <assets>/models/<source>)")
    add("report", "library_report.md")
    return parser.parse_args(argv)


def main(argv=None, client_factory=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["blender-thumbs"]:
        return _bl_thumbs(argv[1])
    args = parse_args(argv)
    try:
        cfg = load_config(Path(args.config) if args.config else None)
        out = Path(args.out)
        if args.command == "survey":
            ds = cfg["dataset"]
            if args.mirror:
                hub = LocalHub(Path(args.mirror))
            else:
                hub = HFHub(ds["repo"], ds["revision"], Path(args.cache) if args.cache else None,
                            ds.get("repo_type", "dataset"))
            doc = survey(hub, out, cfg, download=not args.no_download, workers=args.workers)
            print(f"objaverse survey: {len(doc['candidates'])} candidate(s) -> {out / SURVEY_NAME}")
            return EXIT_OK if doc["candidates"] else EXIT_FAIL
        if args.command == "thumbnails":
            doc, rc = thumbnails(out, Path(args.work) if args.work else None, cfg, blender=args.blender,
                                 deadline=deadline_of(args.deadline), device=args.device)
            print(f"objaverse thumbnails: {doc['counts']} (device {doc['device']}) -> {out / THUMBS_JSON}")
            return rc
        if args.command == "judge-requests":
            doc = judge_requests(out, cfg)
            print(f"objaverse judge-requests: {len(doc['items'])} item(s) -> {out / JUDGE_DIR / REQUESTS_NAME}")
            return EXIT_OK if doc["items"] else EXIT_FAIL
        if args.command == "judge":
            return judge(out, args.model_key, args.server, args.workers, args.deadline, args.seed_answers,
                         client_factory=client_factory, retries=args.retries, timeout_s=args.timeout)
        if args.command == "judge-status":
            summary = judge_status(out)
            if args.json:
                print(json.dumps(summary, indent=1))
            else:
                print(f"objaverse judge-status {out}: {summary['items']} item(s)")
                for key, m in summary["models"].items():
                    print(f"  {key} ({m['slug']}): {m['answered']} answered, {m['stale']} stale, {m['failed']} "
                          f"failed, {m['missing']} missing{' (incomplete)' if m['incomplete'] else ''}")
            return EXIT_OK if summary["complete"] else EXIT_FAIL
        if args.command == "accept":
            sources = None
            if args.sources:
                sources = [s for s in args.sources.replace(",", " ").split() if s]
                unknown = [s for s in sources if s not in SOURCES]
                if unknown:
                    raise UsageError(f"unknown source(s) {', '.join(unknown)} (sources: {', '.join(SOURCES)})")
            doc = accept(out, cfg, sources=sources)
            print(f"library accept ({'all sources' if sources is None else ', '.join(sources)}): {doc['counts']} "
                  f"-> {out / ACCEPTED_NAME}")
            return EXIT_OK if doc["accepted"] else EXIT_FAIL
        if args.command == "write-catalog":
            doc = write_catalog(out, Path(args.assets), cfg)
            return EXIT_OK if doc else EXIT_FAIL
        if args.command == "report":
            report(out, cfg)
            print(f"objaverse report -> {out / REPORT_NAME}")
            return EXIT_OK
    except UsageError as exc:
        print(f"objaverse {args.command}: {exc}", file=sys.stderr)
        return EXIT_SERVER
    raise AssertionError(args.command)


# --------------------------------------------------------------------------
# Blender side (runs inside ``blender -b``; bpy and mathutils exist only there)
# --------------------------------------------------------------------------

def _bl_device(scene, requested: str) -> str:
    """Cycles device: OPTIX, then CUDA, then CPU (as wenart.blender.render.configure_device)."""
    import bpy

    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    device = "CPU"
    if requested != "cpu":
        for dev_type in ("OPTIX", "CUDA"):
            try:
                prefs.compute_device_type = dev_type
                prefs.get_devices()
                if [d for d in prefs.devices if d.type == dev_type]:
                    for d in prefs.devices:
                        d.use = d.type == dev_type
                    scene.cycles.device = "GPU"
                    device = dev_type
                    break
            except Exception as exc:  # noqa: BLE001 - no such backend on this machine
                print(f"{dev_type} not usable: {exc}")
    if device == "CPU":
        scene.cycles.device = "CPU"
    print(f"DEVICE={device}")
    return device


def _bl_world(scene, grey: float) -> None:
    import bpy

    world = bpy.data.worlds.new("thumb_world")
    scene.world = world
    try:
        world.use_nodes = True
    except (AttributeError, TypeError):      # always node-based in newer Blender versions
        pass
    tree = getattr(world, "node_tree", None)
    if tree is None:
        world.color = (grey, grey, grey)
        return
    bg = next((n for n in tree.nodes if n.type == "BACKGROUND"), None)
    if bg is None:
        for n in list(tree.nodes):
            tree.nodes.remove(n)
        out = tree.nodes.new("ShaderNodeOutputWorld")
        bg = tree.nodes.new("ShaderNodeBackground")
        tree.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bg.inputs["Color"].default_value = (grey, grey, grey, 1.0)
    bg.inputs["Strength"].default_value = 1.0


def _bl_measure(bpy, meshes, raw: Optional[list] = None) -> tuple[list, list, dict]:
    """World vertices, polygon records and counts of the imported mesh objects (evaluated, all transforms); with
    ``raw`` (a list) every polygon's world vertices are appended to it too (the deck measurement of a bed)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points, polys = [], []
    counts = {"triangles": 0, "colour_attributes": 0, "images": set()}
    for ob in meshes:
        ev = ob.evaluated_get(depsgraph)
        me = ev.to_mesh()
        try:
            mw = ob.matrix_world
            wv = [tuple(mw @ v.co) for v in me.vertices]
            points.extend(wv)
            for poly in me.polygons:
                vs = [wv[i] for i in poly.vertices]
                polys.append(poly_record(vs))
                counts["triangles"] += max(0, len(vs) - 2)
                if raw is not None:
                    raw.append(vs)
            counts["colour_attributes"] += len(getattr(me, "color_attributes", None) or [])
        finally:
            ev.to_mesh_clear()
        for slot in ob.material_slots:
            mat = slot.material
            tree = getattr(mat, "node_tree", None) if mat is not None else None
            for node in (tree.nodes if tree is not None else []):
                if node.type == "TEX_IMAGE" and node.image is not None:
                    counts["images"].add(node.image.name)
    return points, polys, counts


def _bl_one(bpy, Vector, scene, cam, sun, job: dict, s: dict) -> dict:
    before = {o.name for o in bpy.data.objects}
    bpy.ops.import_scene.gltf(filepath=job["glb"], import_shading="NORMALS", import_scene_as_collection=False,
                              import_select_created_objects=False)
    new = [o for o in bpy.data.objects if o.name not in before]
    meshes = [o for o in new if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("no mesh objects in the GLB")
    for ob in new:
        if ob.type == "LIGHT":                 # a light shipped in the GLB would change the judged look
            ob.hide_render = True
    bpy.context.view_layer.update()
    raw = [] if job.get("deck") else None
    points, polys, counts = _bl_measure(bpy, meshes, raw)
    if not points:
        raise RuntimeError("no vertices in the GLB")
    stats = front_stats(points, polys, s["top_fraction"], s["side_fraction"], s["normal_dot"])
    result = {"stats": stats, "vertices": len(points), "triangles": counts["triangles"], "mesh_objects": len(meshes),
              "images": len(counts["images"]), "colour_attributes": counts["colour_attributes"]}
    if raw is not None:
        result["deck"] = deck_height(raw, stats["bbox_min"], stats["bbox_max"], float(s.get("deck_ray_offset", 0.2)))
    if job.get("render", True) is False:
        return result                          # measured before M8: the views on disk stay
    centre = [(a + b) / 2.0 for a, b in zip(stats["bbox_min"], stats["bbox_max"])]
    dist = camera_distance(stats["extents"], float(s["lens_mm"]), float(s["sensor_mm"]), float(s["margin"]))
    cam.data.clip_start = max(1e-4, dist * 0.01)
    cam.data.clip_end = dist * 10.0
    for i, side in enumerate(VIEW_SIDES):
        loc = view_location(centre, dist, side, float(s["elevation_deg"]))
        cam.location = loc
        cam.rotation_euler = (Vector(centre) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        light = view_direction(side, float(s["sun_elevation_deg"]), float(s["sun_azimuth_offset_deg"]))
        sun.rotation_euler = (-Vector(light)).to_track_quat("-Z", "Y").to_euler()
        scene.render.filepath = job["views"][i]
        bpy.ops.render.render(write_still=True)
    return result


def _bl_clear(bpy, keep: set) -> None:
    for ob in [o for o in bpy.data.objects if o.name not in keep]:
        bpy.data.objects.remove(ob, do_unlink=True)
    try:
        bpy.data.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
    except (AttributeError, TypeError):
        pass


def _bl_thumbs(jobs_path: str) -> int:
    """Measure and render every job of ``blender_jobs.json``; one ``measure/<uid>.json`` per object and
    ``blender_status.json``. Returns 3 when the deadline left objects undone, else 0."""
    import bpy
    from mathutils import Vector

    jobs = json.loads(Path(jobs_path).read_text(encoding="utf-8"))
    s = jobs["settings"]
    deadline = jobs.get("deadline")
    work = Path(jobs["work"])
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    device = _bl_device(scene, s.get("device", "auto"))
    scene.cycles.samples = int(s["samples"])
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = int(s["resolution"])
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    _bl_world(scene, float(s["background"]))
    cam_data = bpy.data.cameras.new("thumb_cam")
    cam_data.lens = float(s["lens_mm"])
    cam_data.sensor_width = float(s["sensor_mm"])
    cam_data.sensor_fit = "AUTO"
    cam = bpy.data.objects.new("thumb_cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    sun_data = bpy.data.lights.new("thumb_sun", "SUN")
    sun_data.energy = float(s["sun_energy"])
    sun_data.angle = math.radians(5.0)
    sun = bpy.data.objects.new("thumb_sun", sun_data)
    scene.collection.objects.link(sun)
    keep = {o.name for o in bpy.data.objects}
    status = {"device": device, "blender": bpy.app.version_string, "done": [], "failed": [], "left": []}
    for job in jobs["objects"]:
        if deadline and time.time() >= float(deadline):
            status["left"].append(job["uid"])
            continue
        t0 = time.time()
        rec = {"uid": job["uid"], "glb": job["glb"], "glb_sha256": job["glb_sha256"], "ok": False, "device": device}
        try:
            rec.update(_bl_one(bpy, Vector, scene, cam, sun, job, s))
            rec["ok"] = True
            status["done"].append(job["uid"])
        except Exception as exc:  # noqa: BLE001 - one broken GLB must not stop the others
            rec["error"] = f"{type(exc).__name__}: {exc}"
            status["failed"].append(job["uid"])
        finally:
            _bl_clear(bpy, keep)
        rec["seconds"] = round(time.time() - t0, 2)
        write_json(Path(job["measure"]), rec)
        print(f"THUMB {job['uid']} {'ok' if rec['ok'] else rec['error']} {rec['seconds']} s", flush=True)
    status["incomplete"] = bool(status["left"])
    write_json(work / "blender_status.json", status)
    return EXIT_DEADLINE if status["left"] else EXIT_OK


if __name__ == "__main__":
    # Inside Blender the arguments follow "--"; as ``python -m`` they are the usual ones.
    sys.exit(main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]))
