"""HSSD doors and windows as library openings (28 Oct 2026, user: "I want better doors inside the house and the
outside, I am not liking that much the models used at the moment, some variation is needed", then "find the best
models").

What: the door and window objects of ``hssd/hssd-models`` (the CC BY-NC 4.0 layer of ``wenart.assets.hssd``, relaxed
licence mode only) typed into the opening categories of ``wenart.blender.opening_models`` (``entrance``, ``door``,
``terrace_door``, ``glazed_door``, ``window`` and, since 28 Oct 2026, ``inside_door``), with their sizes, how they
open and their series, and the growth list of the pod run that audits them (``candidates_hssd_openings.json``,
``approved_hssd_openings.json``: ``scripts/jobs/library_growth.sh`` ``GROWTH_ONLY=openings``).

Evidence (read on 28 Oct 2026, no token: the Hub tree API of ``hssd/hssd-models`` @``hssd.REVISION`` and the object
table ``metadata/fpmodels-with-decomposed.csv`` of ``hssd/hssd-hab`` @``hssd.META_REVISION``):

- ``objects/openings/`` holds 841 GLBs (13-182 KB, 52.6 MB in all): the Floorplanner product models of doors and
  windows in 56 series, ids ``<series>-<variant>`` (``200-19``); every one is a row of the table with its WordNet
  synset and ``aligned.dims`` (x, y up, z: width, height, depth in metres) and none has a name, a tag or a room
  (``notes: openable``). The variants of a series are one product at other sizes (one file size per series): a
  window series runs from 0.4 to 5.4 m wide.
- The hex folders hold a few named door and window products of the same table (``Tim double door``, ``Victorian
  Door White``, ``YOO OH single panel door, EARTH``, ``Door Restoration Hardware``, ``Semi Circular Window``); the
  table's barn doors (``interior_barn_door.n.01``) and the second YOO OH door are not in ``hssd-models``.
- Synsets: ``door.n.01`` (one leaf), ``double_door.n.01``, ``sliding_door.n.01``, ``window.n.01``; left out with the
  reason (``LEFT_OUT_SYNSETS``): garage, revolving, lift and shower doors; a "Mirror" filed as a window.

How (pure; the tests feed a small table):

- ``typed_opening(row)``: one table row -> ``{id, title, name, type, kind, operation, series, variant, w, d, h,
  synset, categories}`` or a record with ``left_out`` (the reason). ``categories`` are the opening categories whose
  real size box (``CATEGORY_SIZES`` = ``opening_models.SIZES`` plus ``inside_door``) holds the model and that its kind
  serves (``KIND_CATEGORIES``); a title is made for a model without a name (``HSSD door 200-19``): the words the
  opening choice reads (``sliding``, ``double``, ``window``) come from the synset.
- ``pick(rows, listing)``: per series a spread over the proportions (``log(w / h)`` in steps of ``PROPORTION_STEP``;
  per step the variant nearest the category's common size, the steps nearest the common proportion first, at most
  ``MAX_PER_SERIES``), every named product that maps, files under ``MIN_OPENING_BYTES`` left out (none of the 841 is).
  The categories and the series are spread by construction; the style families (Scandinavian ... Mediterranean) are
  the audit's vision answer: the table names no style for the Floorplanner models.
- ``list_doc`` is the growth list (the shape of ``hssd.list_doc``); ``main`` writes it from the csv and a listing.

Why: the 3D Warehouse doors and windows are mostly quality 3 of 5 with no 5 (``results/library/audit/3dwh``); after
the title filters about ten fit an entrance and one a terrace door, so every house got the same "Front Door" and
"Aluminium Casement Window". The HSSD furniture rated better than the 3D Warehouse layer in the same audit (4 of 5 for
176 of 852 answers, 3D Warehouse 308 of 3275), and the Floorplanner series come in many sizes, so one product fits a
house's openings without stretching its frames. Infinigen's door and window factories (``PanelDoorFactory``,
``GlassPanelDoorFactory``, ``LiteDoorFactory``, ``LouverDoorFactory``, ``WindowFactory`` in
``tests/assets/list_indoor_meshes.txt`` of the pinned v1.19.0 commit) are left out of this list: the same audit rated
Infinigen's generated furniture 2 of 5 (20 of 27 answers), below ``site_models.MIN_VISION_QUALITY``.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path
from typing import Optional

from wenart.assets import hssd as H

SOURCE_KEY = "hssd_openings"            # the growth list, approval and ingest key; the entries' source is "hssd"
LIST_NAME = f"candidates_{SOURCE_KEY}.json"
OPENINGS_FOLDER = "objects/openings"
SERIES_ID = re.compile(r"^(\d+)-(\d+)$")
MIN_OPENING_BYTES = 10_000              # a door or window GLB below this is a stub (the smallest real one: 13 KB)
SINGLE_DOOR_MAX_M = 1.5                 # = opening_models.SIZES["entrance"] width: a wider door.n.01 is no one leaf
PROPORTION_STEP = 0.2                   # log(w / h) steps of the spread: about 22 % (opening_models.ASPECT_TOL 0.25)
MAX_PER_SERIES = {"door": 6, "window": 10}
# the size of a common product and its proportion per type (designer values): the variant nearest it per step
COMMON_SIZE = {"door": (0.9, 2.1), "window": (1.2, 1.3)}
# synset -> (our type, the opening's kind, how it opens; None: the audit's vision answer says)
SYNSETS: dict[str, tuple[str, str, Optional[str]]] = {
    "door.n.01": ("door", "single", "hinged"),
    "double_door.n.01": ("door", "double", "hinged"),
    "sliding_door.n.01": ("door", "sliding", "sliding"),
    "bi-fold_door.n.01": ("door", "folding", "folding"),
    "interior_barn_door.n.01": ("door", "barn", "sliding"),
    "window.n.01": ("window", "window", None),
}
LEFT_OUT_SYNSETS: dict[str, str] = {
    "garage_door.n.01": "a sectional garage door: the parametric door builds it (opening_models.NO_LIBRARY_KINDS)",
    "revolving_door.n.02": "a revolving door: no door of a house",
    "elevator_door.n.01": "a lift door: no door of a house",
    "shower_door.n.01": "a shower screen or door: a bathroom fixture, not an opening of a wall",
}
LEFT_OUT_WORDS = ("mirror", "garage", "shower")      # a named product the synset files wrongly
KIND_WORDS = {"single": "door", "double": "double door", "sliding": "sliding door", "folding": "folding door",
              "barn": "barn door", "window": "window"}
# the categories each kind serves (opening_models.CATEGORIES and INSIDE_CATEGORY)
KIND_CATEGORIES: dict[str, tuple[str, ...]] = {
    "single": ("entrance", "door", "terrace_door", "inside_door"),
    "double": ("glazed_door",), "sliding": ("glazed_door", "inside_door"), "folding": ("glazed_door",),
    "barn": ("inside_door",), "window": ("window",)}


def category_sizes() -> dict:
    """(width range, height range) of one model per category: ``opening_models.SIZES`` (and its ``inside_door``)."""
    from wenart.blender import opening_models as OM
    return dict(OM.SIZES)


def _floats(text) -> Optional[list[float]]:
    try:
        vals = [float(v) for v in str(text or "").split(",")]
    except ValueError:
        return None
    return vals if len(vals) == 3 and all(math.isfinite(v) and v > 0 for v in vals) else None


def series_of(hid: str) -> tuple[str, Optional[int]]:
    """``(series, variant)`` of an object id: ``200-19`` -> ``("200", 19)``; a hex id is its own series."""
    m = SERIES_ID.match(str(hid))
    if m:
        return m.group(1), int(m.group(2))
    return str(hid)[:12], None


def categories_of(kind: str, w: float, h: float, sizes: Optional[dict] = None) -> list[str]:
    """The categories of ``KIND_CATEGORIES[kind]`` whose size box holds a ``w`` x ``h`` m model (pure)."""
    sizes = sizes if sizes is not None else category_sizes()
    out = []
    for cat in KIND_CATEGORIES.get(kind, ()):
        box = sizes.get(cat)
        if box and box[0][0] <= w <= box[0][1] and box[1][0] <= h <= box[1][1]:
            out.append(cat)
    return out


def title_of(name: str, kind: str, hid: str, w: float, h: float) -> str:
    """The product's name, else ``HSSD <kind words> <id> (w x h m)``: the opening choice reads the kind's words."""
    from wenart.assets.audit.growth_entries import source_text
    name = source_text(name)
    if name:
        return name
    return f"HSSD {KIND_WORDS.get(kind, kind)} {hid} ({w:.2f} x {h:.2f} m)"


def typed_opening(row: dict, sizes: Optional[dict] = None) -> Optional[dict]:
    """One table row as a typed opening (module docstring), a record with ``left_out`` (why), or None (no opening)."""
    synset = str(row.get("wnsynsetkey") or "").strip()
    hid = str(row.get("id") or "").strip()
    if not hid or (synset not in SYNSETS and synset not in LEFT_OUT_SYNSETS and
                   str(row.get("main_category") or "") not in ("door", "window")):
        return None                                     # curtains, blinds, door mats, door bells: no opening
    name = str(row.get("name") or "").strip()
    dims = _floats(row.get("aligned.dims"))
    base = {"id": hid, "name": name, "synset": synset}
    if synset in LEFT_OUT_SYNSETS:
        return dict(base, left_out=LEFT_OUT_SYNSETS[synset])
    if synset not in SYNSETS:
        return dict(base, left_out=f"synset {synset or 'none'}: no opening type of ours")
    if any(w in f" {name.lower()} " for w in LEFT_OUT_WORDS):
        return dict(base, left_out=f"its name {name!r} says it is no door or window of a wall")
    if not dims:
        return dict(base, left_out="no aligned.dims")
    w, h, d = dims                                      # glTF frame: x (width), y (up), z (depth)
    ftype, kind, op = SYNSETS[synset]
    note = None
    if kind == "single" and w > SINGLE_DOOR_MAX_M:
        # a door.n.01 wider than one leaf ("Door Restoration Hardware", 1.75 x 2.61 m): a pair or a leaf with side
        # lights; the audit's leaves and glazing say which, the glazed door category takes it when it is glass
        kind, note = "double", f"door.n.01 {w:.2f} m wide: more than one leaf (a pair or side lights)"
    series, variant = series_of(hid)
    cats = categories_of(kind, w, h, sizes)
    rec = dict(base, type=ftype, kind=kind, operation=op, series=series, variant=variant, w=round(w, 4),
               d=round(d, 4), h=round(h, 4), categories=cats, title=title_of(name, kind, hid, w, h))
    if note:
        rec["kind_note"] = note
    if not cats:
        rec["left_out"] = (f"{w:.2f} x {h:.2f} m fits no {KIND_WORDS.get(kind, kind)} category of a house "
                           f"({', '.join(KIND_CATEGORIES.get(kind, ())) or 'none'})")
    return rec


def _spread(members: list[dict], ftype: str, cap: int) -> list[dict]:
    """The variants of one series spread over the proportions (module docstring)."""
    cw, ch = COMMON_SIZE[ftype]
    common = math.log(cw / ch)
    steps: dict[int, list] = {}
    for m in members:
        a = math.log(m["w"] / m["h"])
        steps.setdefault(int(round(a / PROPORTION_STEP)), []).append(m)
    order = sorted(steps, key=lambda k: (abs(k * PROPORTION_STEP - common), k))
    out = []
    for k in order[:cap]:
        best = min(steps[k], key=lambda m: (abs(math.log(m["h"] / ch)) + abs(math.log(m["w"] / cw)), m["id"]))
        out.append(best)
    return out


def pick(rows: list[dict], listing: dict, sizes: Optional[dict] = None) -> tuple[list[dict], list[dict]]:
    """``(candidates, left out)`` of the table ``rows`` for the objects of ``listing`` (``{id: {"path", "size"}}``:
    the Hub listing of ``hssd-models``): the growth records (``candidate``) and ``{id, name, reason}`` per opening
    left out, both in id order."""
    typed, left = [], []
    for row in rows:
        t = typed_opening(row, sizes)
        if t is None:
            continue
        hid = t["id"]
        if hid not in listing:
            continue                                    # in hssd-hab only (the barn doors): nothing to download
        size = (listing.get(hid) or {}).get("size")
        if t.get("left_out"):
            left.append({"id": hid, "name": t.get("name") or "", "reason": t["left_out"]})
        elif isinstance(size, int) and size < MIN_OPENING_BYTES:
            left.append({"id": hid, "name": t.get("name") or "", "reason": f"a {size} byte stub"})
        else:
            typed.append(t)
    by_series: dict[tuple, list] = {}
    for t in typed:
        by_series.setdefault((t["type"], t["kind"], t["series"]), []).append(t)
    picked = []
    for (ftype, _kind, _series), members in sorted(by_series.items()):
        chosen = _spread(members, ftype, MAX_PER_SERIES[ftype]) if members[0]["variant"] is not None else members
        picked += [candidate(t, listing, len(members)) for t in chosen]
        ids = {t["id"] for t in chosen}
        left += [{"id": t["id"], "name": t.get("name") or "", "reason": f"series {t['series']}: another variant of a "
                  "proportion step it shares (the spread keeps one per step)"} for t in members if t["id"] not in ids]
    picked.sort(key=lambda c: (c["type"], c["opening"]["series"], c["id"]))
    left.sort(key=lambda r: r["id"])
    return picked, left


def candidate(t: dict, listing: dict, series_size: int = 1) -> dict:
    """The growth record of a typed opening (the fields of ``hssd.candidate_records`` plus ``opening``)."""
    from wenart.assets.audit.growth_entries import styles_hint
    hid = t["id"]
    size = (listing.get(hid) or {}).get("size")
    return {"source": H.SOURCE, "list": SOURCE_KEY, "id": H.UID_PREFIX + hid, "hssd_id": hid, "title": t["title"],
            "name": t.get("name") or "", "type": t["type"], "kind": "opening",
            "opening": {"kind": t["kind"], "operation": t["operation"], "series": f"hssd:{t['series']}",
                        "variant": t["variant"], "series_size": series_size, "categories": list(t["categories"]),
                        "synset": t["synset"],
                        "from": "the HSSD object table (synset, aligned.dims); the audit's vision answer adds "
                                "the role, the glazing, the leaf, the operation and the styles",
                        **({"kind_note": t["kind_note"]} if t.get("kind_note") else {})},
            "dims_m": [t["w"], t["d"], t["h"]], "aspect": round(t["w"] / t["h"], 4),
            "styles_hint": styles_hint(t.get("name") or ""), "synset": t["synset"],
            "licence": H.LICENCE, "licence_flag": H.LICENCE_FLAG,
            "path": (listing.get(hid) or {}).get("path") or H.object_path(hid),
            "size_mb": round(size / 1e6, 4) if isinstance(size, int) else None, "pick": True}


def list_doc(cands: list[dict], left: list[dict], queried_utc: str, notes=()) -> dict:
    """The growth list document (the shape of ``hssd.list_doc``) with the counts per type, kind and category."""
    def count(key):
        out: dict = {}
        for c in cands:
            for v in key(c):
                out[v] = out.get(v, 0) + 1
        return dict(sorted(out.items()))
    known = [c["size_mb"] for c in cands if c.get("size_mb")]
    return {"kind": "library_growth_candidates", "source": H.SOURCE, "list": SOURCE_KEY, "queried_utc": queried_utc,
            "query": {"repo": H.REPO_ID, "revision": H.REVISION, "folder": OPENINGS_FOLDER,
                      "metadata": f"{H.META_REPO_ID}:{H.META_FILE}", "metadata_revision": H.META_REVISION,
                      "proportion_step": PROPORTION_STEP, "max_per_series": MAX_PER_SERIES},
            "licences": [H.LICENCE], "licence_flag": H.LICENCE_FLAG, "licence_url": H.LICENCE_URL,
            "gated": {"page": H.PAGE_URL, "prompt": H.GATED_PROMPT,
                      "decision": "D2 of 12 Oct 2026 (docs/milestone13.md §12): the user accepts the terms with the "
                                  "account behind the pod's hf_token secret"},
            "count": len(cands), "picked": sum(1 for c in cands if c.get("pick", True)),
            "picked_size_mb": round(sum(known), 2), "size_known": len(known),
            "by_type": count(lambda c: [c["type"]]), "by_kind": count(lambda c: [c["opening"]["kind"]]),
            "by_category": count(lambda c: c["opening"]["categories"]),
            "series": len({c["opening"]["series"] for c in cands}), "left_out": len(left),
            "notes": list(notes), "candidates": cands, "left_out_records": left}


def load_listing(path) -> dict:
    """``{id: {"path", "size"}}`` from a compact listing or from Hub tree API pages (a list of file records)."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(doc, dict):
        return {str(k): v for k, v in doc.items() if isinstance(v, dict)}
    out = {}
    for x in doc or []:
        if isinstance(x, dict) and x.get("type") == "file" and str(x.get("path", "")).endswith(".glb"):
            out[Path(x["path"]).stem] = {"path": x["path"], "size": x.get("size")}
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m wenart.assets.hssd_openings",
                                description="the HSSD door and window growth list (28 Oct 2026)")
    p.add_argument("--meta", required=True, help="hssd-hab metadata/fpmodels-with-decomposed.csv")
    p.add_argument("--listing", required=True, help="{id: {path, size}} or Hub tree API pages of hssd-models")
    p.add_argument("--out", default="results/library/growth")
    p.add_argument("--queried-utc", required=True)
    args = p.parse_args(argv)
    csv.field_size_limit(1 << 28)
    with Path(args.meta).open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    listing = load_listing(args.listing)
    cands, left = pick(rows, listing)
    in_openings = sum(1 for v in listing.values() if str(v.get("path", "")).startswith(OPENINGS_FOLDER + "/"))
    notes = [f"{len(rows)} metadata rows; {in_openings} GLBs in {OPENINGS_FOLDER}/ of {H.REPO_ID} @{H.REVISION[:7]} "
             f"({len(listing)} objects listed)",
             f"per series a spread over the proportions (log(w / h) steps of {PROPORTION_STEP}), at most "
             f"{MAX_PER_SERIES['door']} doors and {MAX_PER_SERIES['window']} windows a series; every named door and "
             "window product that maps",
             "the Floorplanner openings have no name in the table: their style families come from the audit's vision "
             "answer (the opening question, ask.version_openings)",
             "CC BY-NC 4.0: relaxed licence mode only; the pod skips the ingest with a clear log line on HTTP 403"]
    doc = list_doc(cands, left, args.queried_utc, notes)
    H.write_json(Path(args.out) / LIST_NAME, doc)
    print(f"hssd openings: {doc['count']} picks ({doc['by_type']}, categories {doc['by_category']}), "
          f"{doc['picked_size_mb']} MB, {doc['series']} series, {doc['left_out']} left out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
