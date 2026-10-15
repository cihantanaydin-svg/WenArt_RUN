"""HSSD (Habitat Synthetic Scenes Dataset) as a library source for the relaxed licence mode (docs/milestone13.md §2.1,
§12 D2, §13.2 row ``hssd.py``; track T7).

What: ``hssd/hssd-models`` on Hugging Face holds the real-product object models (Floorplanner catalogue) of HSSD as
GLB files (14,267 GLBs, 38.45 GB; median 1.65 MB, mean 2.70 MB, p90 6.21 MB, the largest 89 MB; read from the Hub
API listing on 15 Oct 2026, ``REVISION``). The repository is gated (``gated: auto``): the user accepts the terms on
``https://huggingface.co/datasets/hssd/hssd-models`` with the account behind the pod's ``HF_TOKEN`` (user decision D2
of 12 Oct 2026). Its licence is CC BY-NC 4.0 (the card: "You agree to use this dataset under the CC BY-NC 4.0 license
terms"), so every HSSD entry carries ``licence_flag: non_commercial`` and is used in ``relaxed`` mode only.

- Layout (verified on the API listing): ``objects/<hex digit>/<40-hex id>.glb`` (16 folders ``0``-``f``), plus
  ``objects/x/`` (ids starting with ``x``) and ``objects/openings/`` (doors and windows, ids like ``200-19``), and
  ``stages/*.glb``; the only other files are ``README.md``, ``.gitattributes`` and ``.gitignore``. There is no metadata
  table in ``hssd-models``; the object table is ``metadata/fpmodels-with-decomposed.csv`` of the public (not gated,
  same licence) companion ``hssd/hssd-hab`` (``META_REPO_ID``): columns ``id, name, wnsynsetkey, up, front, foundIn,
  hasMultipleObjects, support, dims, aligned.dims, simClusterIds, decomposedFrom, decomposedInto,
  floorplanner-category-tags, isArticulatable, main_wnsynsetkey, main_category, super_category, notes``; 20,451 rows,
  every ``hssd-models`` object among them; ``aligned.dims`` = ``x, y, z`` in metres in the glTF frame (``y`` up:
  a queen bed reads ``1.76, 1.20, 2.30``, a fridge ``0.91, 1.77, 0.70``), so width = x, height = y, depth = z.
- ``load_metadata(path)`` reads that csv; ``typed_rows(rows)`` maps every row onto our types by its WordNet synset
  (``SYNSET_TYPES``; beds split at the width ``BED_SPLIT_W``, a plain ``table.n.02`` by size, a ``sink.n.01`` by the
  room, a stool by height, a potted plant by height) with the box as ``(w, d, h)``.
- ``hssd_candidates(demands, n_per_bin, rows=None, used_ids=()) -> [ids]`` (frozen): the HSSD objects that fit the
  demand bins of ``wenart.assets.audit.demands.size_grid`` (per type and bin the ``n_per_bin`` nearest by size, the
  ones inside the fit's caps first, single objects before sets, the id as the tie-break; at most ``MAX_OFF`` off the
  bin, outdoor pieces left out); ``candidate_records`` gives the full records for the growth list.
- ``gate_check(token, ...)`` asks the Hub for one object file with the token: 200 / 302 = the terms are accepted, 401
  = the token is not accepted, 403 = the account has not accepted the terms (the growth job then skips the HSSD step
  with a clear log line, D2). ``download(ids, dest, token_env="HF_TOKEN")`` (frozen) downloads exactly those objects
  with ``huggingface_hub.snapshot_download(repo_id, repo_type="dataset", revision, local_dir, allow_patterns,
  token, max_workers)`` (huggingface_hub 2.0.0 on the pod, ``scripts/pod_requirements.txt``; the signature read on
  https://huggingface.co/docs/huggingface_hub/v2.0.0/package_reference/file_download on 15 Oct 2026), or one file
  at a time over HTTPS when the package is missing; the token is read from the environment only and never printed,
  logged or written.
- ``entry_fields()`` are the licence fields of every HSSD catalogue entry (``growth_entries.hssd_entry``):
  ``licence: "CC-BY-NC-4.0"``, ``licence_flag: "non_commercial"``, ``licence_declared_by: "publisher"``,
  ``licence_url: "https://huggingface.co/datasets/hssd/hssd-models"``, ``commercial_safe: false`` and the attribution
  with the dataset's name and paper (the card states no citation block; the paper page
  https://huggingface.co/papers/2306.11290 names the title and authors, ``CITATION``).

Why: no open commercial-safe source has realistic bath and kitchen fixtures or real products at the drawn sizes
(§2.1); HSSD has them (toilets, basins, tubs, showers, fridges, stoves, 2.5-3 m wardrobes, 3 m tables). The user
chose the relaxed mode for the PoC (D1, D2); every render says whether it is commercial-safe (T8).

How: pure functions on the metadata rows and the demand bins (tests feed a small fake table); the network parts take
injectable fetchers; nothing is deleted; downloads keep complete files (resume).
"""
from __future__ import annotations

import csv
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Optional

REPO_ID = "hssd/hssd-models"
REPO_TYPE = "dataset"
# The commit of the listing read on 15 Oct 2026 (``sha`` of https://huggingface.co/api/datasets/hssd/hssd-models;
# lastModified 2023-06-15): every download is pinned to it.
REVISION = "208ea6bc22d863bbc1cbaef1829b3e646600dfb6"
META_REPO_ID = "hssd/hssd-hab"                    # public (gated: false on the API, 15 Oct 2026), CC BY-NC 4.0 too
META_REVISION = "4369cb9876214c7fbebcf552eb532380e4d287e4"
META_FILE = "metadata/fpmodels-with-decomposed.csv"
HUB = "https://huggingface.co"
RESOLVE = HUB + "/datasets/{repo}/resolve/{rev}/{file}"
PAGE_URL = "https://huggingface.co/datasets/hssd/hssd-models"
PROJECT_URL = "https://3dlg-hcvc.github.io/hssd/"
PAPER_URL = "https://huggingface.co/papers/2306.11290"
LICENCE = "CC-BY-NC-4.0"
LICENCE_FLAG = "non_commercial"
LICENCE_DECLARED_BY = "publisher"
LICENCE_URL = PAGE_URL                            # the card that states the terms (docs/milestone13.md §13.2)
LICENCE_TEXT_URL = "https://creativecommons.org/licenses/by-nc/4.0/"
# The card's extra_gated_prompt as text; on the card the licence name is a markdown link to
# https://creativecommons.org/licenses/by-nc/4.0/ (LICENCE_TEXT_URL), read on the API on 15 Oct 2026.
GATED_PROMPT = "You agree to use this dataset under the CC BY-NC 4.0 license terms"
CITATION = ("Mukul Khanna, Yongsen Mao, Hanxiao Jiang, Sanjay Haresh, Brennan Shacklett, Dhruv Batra, Alexander "
            "Clegg, Eric Undersander, Angel X. Chang, Manolis Savva: \"Habitat Synthetic Scenes Dataset (HSSD-200): "
            "An Analysis of 3D Scene Scale and Realism Tradeoffs for ObjectGoal Navigation\" (arXiv 2306.11290, 2023)")
DATASET_NAME = "HSSD: Habitat Synthetic Scenes Dataset (hssd/hssd-models)"
SOURCE = "hssd"
UID_PREFIX = "hssd_"
USER_AGENT = "wenart-run/0.1 (library growth, HSSD)"
TIMEOUT_S = 120
# Per-object sizes of the listing of 15 Oct 2026 (14,267 GLBs): for the download plan before the speed probe.
FILE_SIZE_MB = {"median": 1.65, "mean": 2.70, "p90": 6.21, "max": 89.19, "total_gb": 38.45, "count": 14267}
MAX_FILE_MB = 120.0
# A GLB below this cannot hold a textured product (the listing's smallest files are 0-5 KB stubs): not picked.
MIN_FILE_BYTES = 50_000
# A bed is single below this width (= wenart/assets/objaverse.yaml bed_split_width_m, the ABO rule's split).
BED_SPLIT_W = 1.275
# A candidate more than this off its bin (the larger relative error of width and depth) is not listed: the fit's
# mean-scale range is 0.85-1.20 and the audit rescales nothing of known units beyond 30 % (audit.yaml size.fix).
MAX_OFF = 0.25
OUTDOOR_WORDS = ("patio", "outdoor", "garden")

# WordNet synset (``wnsynsetkey``) -> our type, or a rule name ending in ``*`` (``_rule_type``). Read from the csv on
# 15 Oct 2026 (counts in the ``hssd-models`` repo: sofa 313, l-shaped couch 49, armchair 238, bed 249 + double bed
# 64, nightstand 170, armoire 119 + wardrobe 18, chest of drawers 229, bookcase 203, tv stand 74, dining table 110,
# table 115, coffee table 166, end table 188, desk 175, chair 174, swivel chair 111, bar stool 55 + 52, bench 103,
# footstool 95 + ottoman 33, chaise longue 37, floor lamp 136, table lamp 251, pendant lamp 191, chandelier 101,
# ceiling lamp 133, potted plant 306, rug 644, throw pillow 416, wall art 1,121, wall mirror 257, vase 143, toilet
# 43, sink 22 + sink cabinet 68, bathtub 84, shower stall 55, refrigerator 54, stove / oven 28, washer 22, kitchen
# island 52, console table 90, buffet 94, china cabinet 44, cabinet 128, shelving 26, shoe rack 13, basket 68, bowl
# 27, tray 32 + 8, candle 16 + 79, book 42, wall clock 87, sculpture 48, throw 30, curtain, blind, shade).
SYNSET_TYPES: dict[str, str] = {
    "sofa.n.01": "sofa", "loveseat.n.01": "sofa", "l-shaped_couch.n.01": "sofa_corner",
    "armchair.n.01": "armchair", "easy_chair.n.01": "armchair", "club_chair.n.01": "armchair",
    "bed.n.01": "bed*", "double_bed.n.01": "bed*", "bunk_bed.n.01": "bunk_bed", "crib.n.01": "crib",
    "chaise_longue.n.01": "chaise", "nightstand.n.01": "nightstand",
    "armoire.n.01": "wardrobe", "wardrobe.n.01": "wardrobe", "chest_of_drawers.n.01": "dresser",
    "bookcase.n.01": "bookshelf", "shelving.n.01": "bookshelf", "tv_stand.n.01": "tv_unit",
    "dining_table.n.01": "table_dining", "table.n.02": "table*", "coffee_table.n.01": "table_coffee",
    "end_table.n.01": "side_table", "desk.n.01": "desk",
    "chair.n.01": "chair", "straight_chair.n.01": "chair", "swivel_chair.n.01": "office_chair",
    "stool.n.01": "stool*", "bar_stool.n.01": "bar_stool", "bar_stool.n.01,chair.n.01": "bar_stool",
    "bench.n.01": "bench", "storage_bench.n.01": "bench", "footstool.n.01": "ottoman", "ottoman.n.03": "ottoman",
    "floor_lamp.n.01": "floor_lamp", "table_lamp.n.01": "table_lamp", "pendant_lamp.n.01": "pendant_light",
    "chandelier.n.01": "pendant_light", "ceiling_lamp.n.01": "ceiling_light",
    "potted_plant.n.01": "plant*", "rug.n.01": "rug", "throw_pillow.n.01": "cushion", "throw.n.04": "throw",
    "wall_art.n.01": "wall_art", "wall_mirror.n.01": "mirror", "mirror.n.01": "mirror",
    "vase.n.01": "vase", "flower_in_vase.n.01": "vase",
    "toilet.n.02": "toilet", "sink.n.01": "sink*", "sink_cabinet.n.01": "sink*", "bathtub.n.01": "bathtub",
    "shower_stall.n.01": "shower", "refrigerator.n.01": "fridge", "stove.n.01,oven.n.01": "stove",
    "washer.n.03": "washing_machine", "kitchen_island.n.01": "kitchen_island",
    "console_table.n.01": "console_table", "buffet.n.01": "sideboard", "credenza.n.01": "sideboard",
    "china_cabinet.n.01": "display_cabinet", "cabinet.n.01": "cabinet*", "shoe_rack.n.01": "shoe_cabinet",
    "basket.n.01": "basket", "bowl.n.01": "bowl", "cafeteria_tray.n.01": "tray", "tray.n.01": "tray",
    "candle.n.01": "candle", "candlestick.n.01,candle.n.01": "candle", "candle.n.01,candlestick.n.01": "candle",
    "book.n.02": "books", "wall_clock.n.01": "clock", "sculpture.n.01": "sculpture",
    "window_curtain.n.01": "curtain", "window_blind.n.01": "blind", "window_shade.n.01": "blind",
}
DECOR_TYPES: tuple[str, ...] = ("table_lamp", "pendant_light", "ceiling_light", "plant_small", "plant_large", "plant",
                                "rug", "cushion", "throw", "wall_art", "mirror", "vase", "basket", "bowl", "tray",
                                "candle", "books", "clock", "sculpture", "curtain", "blind")


# --------------------------------------------------------------------------
# Metadata
# --------------------------------------------------------------------------

def metadata_dir(value=None) -> Path:
    return Path(value or os.environ.get("WENART_HSSD_META") or "~/.cache/wenart/hssd").expanduser()


def metadata_path(folder=None) -> Path:
    return metadata_dir(folder) / Path(META_FILE).name


def resolve_url(file: str, repo: str = REPO_ID, revision: str = REVISION) -> str:
    return RESOLVE.format(repo=repo, rev=revision, file=file)


def fetch_metadata(folder=None, fetch: Optional[Callable] = None) -> Path:
    """The object table of ``hssd-hab`` (public: no token) into ``folder`` (kept when present)."""
    dest = metadata_path(folder)
    if dest.is_file() and dest.stat().st_size > 0:
        return dest
    (fetch or fetch_file)(resolve_url(META_FILE, META_REPO_ID, META_REVISION), dest, None)
    return dest


def _floats(text: str) -> Optional[list[float]]:
    try:
        vals = [float(v) for v in str(text or "").split(",")]
    except ValueError:
        return None
    return vals if len(vals) == 3 and all(math.isfinite(v) for v in vals) else None


def load_metadata(path=None) -> list[dict]:
    """The rows of the object table (``csv.DictReader``; the column names as in the file)."""
    p = Path(path) if path else metadata_path()
    if not p.is_file():
        raise FileNotFoundError(f"{p}: the HSSD object table is not downloaded (hssd.fetch_metadata)")
    csv.field_size_limit(1 << 28)
    with p.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _rule_type(rule: str, w: float, d: float, h: float, found_in: str) -> Optional[str]:
    if rule == "bed*":
        return "bed_single" if min(w, d) < BED_SPLIT_W else "bed_double"
    if rule == "table*":
        if h <= 0.55 and max(w, d) >= 0.7:
            return "table_coffee"
        if max(w, d) >= 1.15 and h >= 0.65:
            return "table_dining"
        return "side_table"
    if rule == "sink*":
        return "sink_kitchen" if "kitchen" in found_in else "washbasin"
    if rule == "stool*":
        return "bar_stool" if h >= 0.6 else "ottoman"
    if rule == "plant*":
        if h >= 1.2:
            return "potted_plant"
        return "plant_large" if h >= 0.5 else "plant_small"
    if rule == "cabinet*":
        return "tall_cabinet" if h >= 1.4 else None
    return None


def typed_row(row: dict) -> Optional[dict]:
    """One metadata row as a typed candidate base ``{id, title, type, kind, w, d, h, synset, found_in, multi,
    articulated, outdoor, tags}`` or None (no type of ours, no size)."""
    synset = str(row.get("wnsynsetkey") or "").strip()
    mapped = SYNSET_TYPES.get(synset)
    dims = _floats(row.get("aligned.dims"))
    if not mapped or not dims or min(dims) <= 0:
        return None
    w, h, d = dims                                   # glTF frame: x, y (up), z
    found_in = str(row.get("foundIn") or "").lower()
    ftype = _rule_type(mapped, w, d, h, found_in) if mapped.endswith("*") else mapped
    if not ftype:
        return None
    hid = str(row.get("id") or "").strip()
    if not hid:
        return None
    return {"id": hid, "title": str(row.get("name") or "").strip(), "type": ftype,
            "kind": "decor" if ftype in DECOR_TYPES else "furniture",
            "w": round(w, 4), "d": round(d, 4), "h": round(h, 4), "synset": synset, "found_in": found_in,
            "multi": str(row.get("hasMultipleObjects") or "").lower() == "true",
            "articulated": str(row.get("isArticulatable") or "").lower() == "true",
            "outdoor": any(word in found_in for word in OUTDOOR_WORDS),
            "tags": str(row.get("floorplanner-category-tags") or "")}


def typed_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        t = typed_row(r)
        if t:
            out.append(t)
    return out


# --------------------------------------------------------------------------
# Candidates by demand bin
# --------------------------------------------------------------------------

def object_path(hid: str, listing: Optional[dict] = None) -> str:
    """The repo path of an object: the listing's (``{id: path}``) when given, else by the layout (hex ids under
    their first digit, ``x`` ids under ``objects/x``)."""
    if listing and hid in listing:
        return listing[hid]
    if re.fullmatch(r"[0-9a-f]{40}", hid):
        folder = hid[0]
    elif hid.startswith("x"):
        folder = "x"
    else:
        folder = "openings"                       # doors and windows (ids like 200-19), never picked
    return f"objects/{folder}/{hid}.glb"


def allow_pattern(hid: str) -> str:
    return f"objects/*/{hid}.glb"


def _off(w: float, d: float, bw: float, bd: float) -> float:
    if min(w, d, bw, bd) <= 0:
        return math.inf
    return max(abs(math.log(w / bw)), abs(math.log(d / bd)))


def candidate_records(demands: list[dict], n_per_bin: int = 10, rows: Optional[list[dict]] = None,
                      used_ids=(), *, n_per_bin_decor: Optional[int] = None, sizes: Optional[dict] = None,
                      listing: Optional[dict] = None, max_off: float = MAX_OFF) -> list[dict]:
    """The HSSD candidates of every demand bin (module docstring): ``rows`` are metadata rows (``load_metadata``
    when None); ``used_ids`` are ids (with or without the ``hssd_`` prefix) already in the library; ``sizes``
    ``{id: bytes}`` and ``listing`` ``{id: path}`` come from the Hub listing when known."""
    from wenart.assets.audit import demands as D
    typed = typed_rows(load_metadata() if rows is None else rows)
    used = {str(u)[len(UID_PREFIX):] if str(u).startswith(UID_PREFIX) else str(u) for u in used_ids}
    by_type: dict[str, list[dict]] = {}
    for t in typed:
        if t["id"] in used or (t["outdoor"] and t["kind"] == "furniture" and t["type"] != "potted_plant"):
            continue
        if listing is not None and t["id"] not in listing:
            continue                                  # not in the hssd-models repo (hssd-hab only)
        if sizes is not None and sizes.get(t["id"], MIN_FILE_BYTES) < MIN_FILE_BYTES:
            continue                                  # an empty or stub GLB in the listing (0-5 KB files exist)
        by_type.setdefault(t["type"], []).append(t)
    n_decor = n_per_bin if n_per_bin_decor is None else int(n_per_bin_decor)
    grid = D.size_grid(demands)
    picked: dict[str, dict] = {}
    for ftype, bins in grid.items():
        pool = by_type.get(ftype) or []
        if not pool:
            continue
        h_range = D.height_range(ftype)
        for b in bins:
            if not b.get("demand"):
                continue
            scored = []
            for t in pool:
                if t["id"] in picked:
                    continue
                off = min(_off(t["w"], t["d"], b["w"], b["d"]), _off(t["d"], t["w"], b["w"], b["d"]))
                if off > math.log(1.0 + max_off):
                    continue
                fits = D.covers([t["w"], t["d"], t["h"]], b["w"], b["d"], h_range)
                scored.append((0 if fits else 1, 1 if t["multi"] else 0, round(off, 6), t["id"], t, fits, off))
            scored.sort(key=lambda s: s[:4])
            n_take = n_decor if ftype in DECOR_TYPES else n_per_bin
            for _f, _m, _o, hid, t, fits, off in scored[:n_take]:
                size = (sizes or {}).get(hid)
                picked[hid] = {"source": SOURCE, "id": UID_PREFIX + hid, "hssd_id": hid, "title": t["title"],
                               "type": ftype, "kind": t["kind"], "bin": b["bin"], "bin_label": b.get("label") or "",
                               "demand": b["demand"], "projects": list(b.get("projects") or []),
                               "dims_m": [t["w"], t["d"], t["h"]], "fits_caps": fits,
                               "off": round(math.exp(off) - 1.0, 3), "multi": t["multi"],
                               "articulated": t["articulated"], "found_in": t["found_in"], "synset": t["synset"],
                               "licence": LICENCE, "licence_flag": LICENCE_FLAG,
                               "path": object_path(hid, listing),
                               "size_mb": round(size / 1e6, 3) if size else None, "pick": True}
    out = list(picked.values())
    out.sort(key=lambda r: (r["kind"] != "furniture", r["type"], r["bin"], r["id"]))
    return out


def hssd_candidates(demands: list[dict], n_per_bin: int = 10, rows: Optional[list[dict]] = None, used_ids=(),
                    **kwargs) -> list[str]:
    """The ids (``hssd_<40 hex>``) of ``candidate_records`` (docs/milestone13.md §13.2)."""
    return [r["id"] for r in candidate_records(demands, n_per_bin, rows, used_ids, **kwargs)]


def list_doc(cands: list[dict], demands: list[dict], queried_utc: str, n_per_bin: int, notes=()) -> dict:
    """The growth list document of the candidates (as ``growth.list_doc``, with the demand summary and the
    download estimate)."""
    by_type: dict = {}
    for c in cands:
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1
    known = [c["size_mb"] for c in cands if c.get("size_mb")]
    est = round(sum(known) + (len(cands) - len(known)) * FILE_SIZE_MB["mean"], 1)
    return {"kind": "library_growth_candidates", "source": SOURCE, "queried_utc": queried_utc,
            "query": {"repo": REPO_ID, "revision": REVISION, "metadata": f"{META_REPO_ID}:{META_FILE}",
                      "metadata_revision": META_REVISION, "n_per_bin": n_per_bin, "max_off": MAX_OFF},
            "licences": [LICENCE], "licence_flag": LICENCE_FLAG, "licence_url": LICENCE_URL,
            "gated": {"page": PAGE_URL, "prompt": GATED_PROMPT, "decision": "D2 of 12 Oct 2026 (docs/milestone13.md "
                      "§12): the user accepts the terms with the account behind the pod's hf_token secret"},
            "count": len(cands), "picked": sum(1 for c in cands if c.get("pick", True)),
            "picked_size_mb": est, "size_known": len(known), "picked_by_type": dict(sorted(by_type.items())),
            "demands": {"pieces": sum(d["count"] for d in demands), "rows": len(demands)},
            "notes": list(notes), "candidates": cands}


# --------------------------------------------------------------------------
# The gate and the download (the token never leaves the environment)
# --------------------------------------------------------------------------

def token_from(token_env: str = "HF_TOKEN", env: Optional[dict] = None) -> Optional[str]:
    env = os.environ if env is None else env
    value = env.get(token_env)
    return str(value).strip() or None if value else None


def _request(url: str, token: Optional[str], method: str = "GET") -> urllib.request.Request:
    headers = {"User-Agent": USER_AGENT}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers, method=method)


def head_status(url: str, token: Optional[str], timeout: float = 30.0) -> int:
    """The HTTP status of a HEAD request (redirects not followed: 302 counts as reachable)."""
    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(_request(url, token, "HEAD"), timeout=timeout) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as exc:
        return int(exc.code)


def gate_check(token: Optional[str], probe_id: str = "0001fb06b075a743e6289236cf049df3ad5dfa9c",
               head: Optional[Callable] = None, revision: str = REVISION) -> dict:
    """``{"ok", "status", "reason"}``: whether the token's account may download the gated objects (module
    docstring). ``head(url, token) -> status`` is injectable (tests)."""
    if not token:
        return {"ok": False, "status": None, "reason": "no HF_TOKEN in the environment: the HSSD step is skipped"}
    url = resolve_url(object_path(probe_id), REPO_ID, revision)
    try:
        status = int((head or head_status)(url, token))
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"ok": False, "status": None, "reason": f"the Hub did not answer: {type(exc).__name__}: {exc}"}
    if status in (200, 302, 303, 307):
        return {"ok": True, "status": status, "reason": "terms accepted: the gated objects are reachable"}
    if status == 401:
        return {"ok": False, "status": 401, "reason": "HTTP 401: the Hub does not accept the token (wrong or expired "
                                                      "HF_TOKEN)"}
    if status == 403:
        return {"ok": False, "status": 403, "reason": f"HTTP 403: the account behind HF_TOKEN has not accepted the "
                                                      f"terms at {PAGE_URL} (D2): the HSSD step is skipped"}
    return {"ok": False, "status": status, "reason": f"HTTP {status} from the Hub for the probe object"}


def fetch_file(url: str, dest: Path, token: Optional[str], max_bytes: float = MAX_FILE_MB * 1e6,
               timeout: float = TIMEOUT_S) -> Path:
    """One file over HTTPS (``.part`` then rename, so a present file is complete); ``ValueError`` over
    ``max_bytes``."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    got = 0
    with urllib.request.urlopen(_request(url, token), timeout=timeout) as resp, part.open("wb") as out:
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            got += len(chunk)
            if got > max_bytes:
                out.close()
                part.unlink(missing_ok=True)
                raise ValueError(f"{dest.name}: more than {max_bytes / 1e6:.0f} MB")
            out.write(chunk)
    part.replace(dest)
    return dest


def present(ids: list[str], dest: Path) -> dict[str, Path]:
    """``{id: path}`` of the objects already under ``dest/objects/*/``."""
    out = {}
    root = Path(dest) / "objects"
    for hid in ids:
        hits = sorted(root.glob(f"*/{hid}.glb")) if root.is_dir() else []
        if hits:
            out[hid] = hits[0]
    return out


def _snapshot(ids: list[str], dest: Path, token: str, revision: str, max_workers: int):
    """``snapshot_download`` of exactly these objects (the real package; replaced in tests)."""
    from huggingface_hub import snapshot_download
    return snapshot_download(repo_id=REPO_ID, repo_type=REPO_TYPE, revision=revision, local_dir=str(dest),
                             allow_patterns=[allow_pattern(h) for h in ids], token=token, max_workers=max_workers)


def _hub_status(exc) -> Optional[int]:
    resp = getattr(exc, "response", None)
    code = getattr(resp, "status_code", None)
    return int(code) if isinstance(code, int) else None


def download(ids: list[str], dest, token_env: str = "HF_TOKEN", *, revision: str = REVISION, max_workers: int = 8,
             env: Optional[dict] = None, snapshot: Optional[Callable] = None, fetch: Optional[Callable] = None,
             head: Optional[Callable] = None, listing: Optional[dict] = None, log: Callable = print) -> dict:
    """Download the objects ``ids`` (``hssd_`` prefix allowed) into ``dest`` (``objects/<folder>/<id>.glb``, the
    repo layout). Returns ``{"ok": [ids], "missing": [ids], "kept": n, "gate": gate record, "skipped": bool,
    "error": text | None, "seconds", "bytes", "token_set": bool}``. The token comes from ``env[token_env]`` (the
    process environment by default) and is never part of the record or any message. ``snapshot`` / ``fetch`` /
    ``head`` are injectable (tests); without ``huggingface_hub`` the files come one by one over HTTPS."""
    t0 = time.time()
    dest = Path(dest)
    hids = [str(i)[len(UID_PREFIX):] if str(i).startswith(UID_PREFIX) else str(i) for i in ids]
    token = token_from(token_env, env)
    rec: dict = {"ok": [], "missing": list(hids), "kept": 0, "gate": None, "skipped": False, "error": None,
                 "seconds": 0.0, "bytes": 0, "token_set": bool(token), "revision": revision}
    have = present(hids, dest)
    rec["kept"] = len(have)
    todo = [h for h in hids if h not in have]
    if todo:
        gate = gate_check(token, head=head, revision=revision)
        rec["gate"] = gate
        if not gate["ok"]:
            rec["skipped"] = True
            log(f"hssd: skipped: {gate['reason']}")
            todo = []
    if todo:
        try:
            if snapshot is not None or fetch is None and _hub_available():
                (snapshot or _snapshot)(todo, dest, token, revision, max_workers)
            else:
                for h in todo:
                    path = dest / object_path(h, listing)
                    (fetch or fetch_file)(resolve_url(object_path(h, listing), REPO_ID, revision), path, token)
        except Exception as exc:  # noqa: BLE001 - recorded, never raised with the token in it
            status = _hub_status(exc)
            name = type(exc).__name__
            if status == 403 or name == "GatedRepoError":
                rec["gate"] = {"ok": False, "status": 403, "reason": f"HTTP 403 during the download: the terms at "
                                                                    f"{PAGE_URL} are not accepted (D2)"}
                rec["skipped"] = True
                log(f"hssd: skipped: {rec['gate']['reason']}")
            else:
                rec["error"] = f"{name}: {_scrub(str(exc), token)}"
                log(f"hssd: download error: {rec['error']}")
    have = present(hids, dest)
    rec["ok"] = [h for h in hids if h in have]
    rec["missing"] = [h for h in hids if h not in have]
    rec["bytes"] = sum(p.stat().st_size for p in have.values())
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def _hub_available() -> bool:
    try:
        import huggingface_hub  # noqa: F401
    except ImportError:
        return False
    return True


def _scrub(text: str, token: Optional[str]) -> str:
    return text.replace(token, "<token>") if token else text


# --------------------------------------------------------------------------
# Catalogue fields
# --------------------------------------------------------------------------

def entry_fields() -> dict:
    """The licence fields of every HSSD catalogue entry (docs/milestone13.md §13.2, §13.3)."""
    return {"licence": LICENCE, "licence_flag": LICENCE_FLAG, "licence_declared_by": LICENCE_DECLARED_BY,
            "licence_url": LICENCE_URL, "commercial_safe": False}


def attribution(title: str, hid: str) -> str:
    return (f"\"{title or hid}\" from {DATASET_NAME}, CC BY-NC 4.0 ({LICENCE_TEXT_URL}), {PAGE_URL} "
            f"(object {hid}; {PROJECT_URL}); {CITATION}; changes: scaled to the drawn footprint, re-oriented, "
            "rendered, AI-retouched; PoC use in relaxed licence mode only (non-commercial)")


DATASET = {"name": DATASET_NAME, "owner": "the HSSD authors (3dlg-hcvc, Meta FAIR)", "page": PAGE_URL,
           "project": PROJECT_URL, "paper": PAPER_URL, "citation": CITATION, "licence": LICENCE,
           "licence_url": LICENCE_TEXT_URL, "licence_flag": LICENCE_FLAG, "gated": GATED_PROMPT,
           "revision": REVISION, "metadata": f"{META_REPO_ID}:{META_FILE} @{META_REVISION[:7]}",
           "note": "CC BY-NC 4.0 (the dataset card); used in relaxed licence mode only (user decision D1/D2 of 12 Oct "
                   "2026, docs/milestone13.md §12); every render that shows an HSSD model is commercial-safe: no"}


def write_json(path, doc) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path
