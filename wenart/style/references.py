"""Style reference photos from the internet (27 Oct 2026; user: "Rooms are not looking like the stylish rooms you can
see in the internet, similarly a veranda is not like a veranda ... take the good style photos from the internet and
figure out what needs to be done", lesson UL42).

What:

- ``SPACES``: the kinds of space a reference set is gathered for (living, bedroom, kitchen, ... and the outdoor ones:
  veranda, terrace, balcony, garden, facade), each with the words a photo search uses. ``space_of(room_type,
  subtype, outdoor)`` maps a building's room (or outdoor space) to one.
- ``queries(space, family)``: the search texts for a space in a style family (``"scandinavian living room
  interior"``, ...), the family's own words first.
- ``openverse_search`` / ``commons_search``: photographs under Creative Commons licences from the Openverse API
  (api.openverse.org, no key) and Wikimedia Commons, as candidate records ``{source, id, url, thumb, title, creator,
  licence, licence_url, landing_url, width, height}``. Pure but for ``http`` (a callable ``url -> bytes``, injected
  in tests).
- ``select(cands, scores, k)``: the reference set from the candidates' scores (``score_images``: SigLIP 2 on the pod,
  ``EMBED_MODEL``): photos of the space (not a plan, a render, a product shot, people, an empty or messy room), the
  best style match and photo quality first, near duplicates out (pure).
- ``fetch_set(space, family, root, ...)``: candidates -> downloads -> scores -> the ``K_REFERENCES`` kept, written to
  ``<root>/<space>/<family>/`` with ``manifest.json``; a set already there is reused (the network volume keeps them
  across runs and projects).

The photos guide the AI only (what a good room of the type and style holds, ``wenart.style.recipe``; the judge's
side-by-side look): they are never rendered, built or shown as the project's. Every photo keeps its source, author,
licence and page (``ATTRIBUTION.md`` lists them). Openverse and Wikimedia are not on the cloud session's proxy
allow-list: the pod fetches them (docs/style_references.md).
"""
from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Callable, Optional

# space key -> (photo words, interior?)
SPACES: dict[str, tuple[tuple[str, ...], bool]] = {
    "living": (("living room",), True),
    "dining": (("dining room",), True),
    "kitchen": (("kitchen",), True),
    "bedroom": (("bedroom",), True),
    "child": (("kids bedroom", "children's room"), True),
    "bathroom": (("bathroom",), True),
    "office": (("home office", "study room"), True),
    "hall": (("entryway", "hallway"), True),
    "dressing": (("walk-in closet", "dressing room"), True),
    "veranda": (("covered veranda", "porch"), False),
    "terrace": (("terrace", "patio"), False),
    "balcony": (("balcony",), False),
    "garden": (("garden", "backyard landscaping"), False),
    "facade": (("house exterior", "villa exterior"), False),
}
ROOM_SPACE = {"living": "living", "salon": "living", "dining": "dining", "kitchen": "kitchen", "bedroom": "bedroom",
              "bathroom": "bathroom", "wc": "bathroom", "shower": "bathroom", "office": "office", "study": "office",
              "hall": "hall", "corridor": "hall", "entrance": "hall", "vestibule": "hall", "landing": "hall",
              "storage": "dressing", "dressing": "dressing", "other": "hall"}
OUTDOOR_SPACE = {"veranda": "veranda", "porch": "veranda", "covered": "veranda", "terrace": "terrace",
                 "patio": "terrace", "balcony": "balcony", "garden": "garden", "yard": "garden"}
# the family's own words in a search (the vocabulary's families, wenart/style/vocabulary.py STYLE_FAMILIES)
FAMILY_WORDS: dict[str, tuple[str, ...]] = {
    "scandinavian": ("scandinavian", "nordic"), "japandi": ("japandi",), "modern minimal": ("minimalist", "modern"),
    "minimal": ("minimalist",), "modern": ("modern", "contemporary"), "industrial": ("industrial", "loft"),
    "mediterranean": ("mediterranean",), "classic": ("classic", "traditional"), "rustic": ("rustic", "farmhouse"),
}
# 27 Oct 2026 (review: the caption ranking and filter knew one look, modern and light: "modern", "minimalist", "white
# walls" scored for every family, "vintage", "antique" and "historic" were always out and a facade had to be a
# "modern / contemporary / white ... house", so a classic, rustic or mediterranean family lost its own photos; user
# rule: "every fix is general"). Each family of ``FAMILY_WORDS`` (the vocabulary's STYLE_FAMILIES) has its own caption
# vocabulary: ``look`` (one point each in a caption), ``house`` (the words before "house" / "home" / "villa" of its
# facades), ``buildings`` (its own words for a house: a rustic farmhouse or cottage) and ``period`` (the words of
# ``PERIOD_WORDS`` its rooms carry, so they are no reason to drop a caption). A family's own words of ``FAMILY_WORDS``
# count ``FAMILY_WORD_POINTS``; ``QUALITY_WORDS`` (a well-made photo of any style) count one point for every family.
# Scandinavian keeps the old one-look words (its sets rank as before).
FAMILY_CAPTION: dict[str, dict[str, tuple[str, ...]]] = {
    "scandinavian": {"look": ("modern", "contemporary", "minimalist", "wooden", "light", "white walls"),
                     "house": ("modern", "contemporary", "white", "wooden", "timber"), "buildings": (),
                     "period": ()},
    "japandi": {"look": ("minimalist", "japanese", "zen", "wabi-sabi", "wooden", "oak", "natural materials", "linen",
                         "neutral tones", "calm"),
                "house": ("modern", "contemporary", "japanese", "wooden", "timber", "minimalist"), "buildings": (),
                "period": ()},
    "modern minimal": {"look": ("minimal", "minimalist", "contemporary", "clean lines", "sleek", "uncluttered",
                                "white walls", "light"),
                       "house": ("modern", "contemporary", "minimalist", "white", "concrete"), "buildings": (),
                       "period": ()},
    "minimal": {"look": ("minimal", "minimalist", "contemporary", "clean lines", "sleek", "uncluttered", "white walls",
                         "light"),
                "house": ("modern", "contemporary", "minimalist", "white", "concrete"), "buildings": (),
                "period": ()},
    "modern": {"look": ("contemporary", "minimalist", "sleek", "clean lines", "open plan", "white walls", "light"),
               "house": ("modern", "contemporary", "white", "glass", "concrete"), "buildings": (), "period": ()},
    "industrial": {"look": ("loft", "exposed brick", "brick", "concrete", "metal", "steel", "leather", "warehouse",
                            "exposed beams", "edison"),
                   "house": ("industrial", "brick", "concrete", "steel", "modern"), "buildings": ("loft",),
                   "period": ("vintage",)},
    "mediterranean": {"look": ("whitewashed", "terracotta", "rattan", "wicker", "arched", "stucco", "tile", "olive",
                               "linen", "coastal", "spanish", "greek", "tuscan", "provencal"),
                      "house": ("whitewashed", "white", "spanish", "greek", "tuscan", "stucco", "stone", "coastal"),
                      "buildings": (), "period": ("vintage", "antique", "historic", "historical")},
    "classic": {"look": ("panelled", "paneled", "moulding", "molding", "chandelier", "fireplace", "antique",
                         "vintage", "tufted", "velvet", "parquet", "herringbone", "georgian", "victorian"),
                "house": ("traditional", "colonial", "georgian", "victorian", "brick", "stone", "historic"),
                "buildings": ("townhouse", "manor house"), "period": ("vintage", "antique", "historic", "historical")},
    "rustic": {"look": ("country", "cottage", "wooden", "reclaimed wood", "exposed beams", "beams", "stone",
                        "fireplace", "barn", "log", "vintage", "antique"),
               "house": ("country", "stone", "wooden", "log", "timber", "old"), "buildings": ("farmhouse", "cottage"),
               "period": ("vintage", "antique", "historic", "historical")},
}
FAMILY_WORD_POINTS = 3          # a caption that names the family outranks one with two look words of any family
QUALITY_WORDS = ("cozy", "bright", "stylish", "elegant", "plants", "natural light", "spacious", "well-lit",
                 "interior design", "styled")
K_REFERENCES = 8                # photos kept per space and family
CANDIDATES = 60                 # candidates scored per space and family
MIN_SIDE_PX = 700               # a photo smaller than this both ways is too small to read a room from
DUPLICATE_COS = 0.95            # two photos this similar (image embeddings) are one
EMBED_MODEL = "google/siglip2-so400m-patch14-384"     # Apache-2.0 (checked on the Hub 27 Oct 2026)
EMBED_MODEL_CPU = "google/siglip2-base-patch16-224"   # Apache-2.0: the CPU choice (a fetch in the cloud session)
NEGATIVES = ("a floor plan or a drawing", "a 3D render or a computer graphic", "a product photo on a white background",
             "a photo of people", "an empty unfurnished room", "a messy cluttered room", "a text document or a sign",
             # 27 Oct 2026 (job 150744's bathrooms, dining rooms and bedrooms): rooms that are no home's
             "a public restroom with urinals or rows of sinks", "a restaurant or a hotel dining hall",
             "a museum period room", "a furniture store showroom", "a painting",
             # 27 Oct 2026 (job 175301's dressing rooms were clothing shops)
             "a clothing shop or a market stall")
QUALITY_TEXT = "a beautiful professional interior design photo, magazine quality"
QUALITY_TEXT_OUTDOOR = "a beautiful professional architecture and landscape photo, magazine quality"
OPENVERSE_PAGE_MAX = 20        # pod run 123917: an anonymous Openverse search takes at most 20 results a page
REQUEST_GAP_S = 1.0            # between two searches (the APIs' anonymous rate limits)
RETRIES = 3                    # a 429 / 5xx answer is retried after 2, 4, 8 s
PREFETCH_BUDGET_S = 600.0     # pod run 130756: 25 min of timeouts; the prefetch stops after this (27 Oct 2026: the
                              # automatic Pexels sets of a new family take about 5 min once, then the volume keeps them)
DEAD_SETS = 2                 # ... or when the first sets found nothing at all (the sources are unreachable)
REPO_SETS = Path(__file__).resolve().parents[2] / "assets" / "references"   # curated sets committed with the code
OPENVERSE = "https://api.openverse.org/v1/images/"
COMMONS = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "WenArt-RUN/1.0 (style reference research; https://github.com/cihantanaydin-svg/WenArt_RUN)"


def space_of(room_type: Optional[str], subtype: Optional[str] = None, outdoor: Optional[str] = None) -> Optional[str]:
    """The reference space of a room (``room_type``, ``room_subtype`` "child" -> child) or of an outdoor space kind
    (``outdoor``: veranda / porch / terrace / patio / balcony / garden), None when none fits."""
    if outdoor:
        words = re.findall(r"[a-z]+", str(outdoor).lower())
        return next((OUTDOOR_SPACE[w] for w in words if w in OUTDOOR_SPACE), None)
    if subtype == "child":
        return "child"
    return ROOM_SPACE.get(str(room_type or "").lower())


def queries(space: str, family: Optional[str]) -> list[str]:
    """The search texts of ``space`` in ``family`` (each family word x each space word; the interior ones end with
    "interior"); a family the table does not hold searches the space alone."""
    words, interior = SPACES[space]
    fam = FAMILY_WORDS.get(str(family or "").lower(), ())
    tail = " interior" if interior else ""
    out = [f"{f} {w}{tail}" for f in fam for w in words] or [f"{w}{tail} design" for w in words]
    return list(dict.fromkeys(out))


def broad_queries(space: str, family: Optional[str]) -> list[str]:
    """Fewer words when the family queries found too little (pod run 123917: no photo at all): the family and the
    space (``"scandinavian living room"``), then the space alone (``"living room"``)."""
    words, _interior = SPACES[space]
    fam = FAMILY_WORDS.get(str(family or "").lower(), ())
    out = [f"{fam[0]} {words[0]}"] if fam else []
    return list(dict.fromkeys(out + [w for w in words]))


def _get_json(http: Callable[[str], bytes], url: str) -> dict:
    return json.loads(http(url).decode("utf-8"))


def default_http(url: str, timeout: float = 15.0) -> bytes:
    """GET ``url`` with the project's User-Agent; a 429 or 5xx answer is retried ``RETRIES`` times (2, 4, 8 s)."""
    import time
    import urllib.error

    for attempt in range(RETRIES + 1):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, image/*"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:      # noqa: S310 - https only, fixed hosts
                return resp.read()
        except urllib.error.HTTPError as exc:
            if attempt < RETRIES and (exc.code == 429 or exc.code >= 500):
                time.sleep(2.0 * 2 ** attempt)
                continue
            body = exc.read()[:200].decode("utf-8", "replace") if hasattr(exc, "read") else ""
            raise RuntimeError(f"HTTP {exc.code} {exc.reason}: {body}") from exc
    raise RuntimeError("unreachable")


def openverse_search(query: str, n: int, http: Callable[[str], bytes]) -> list[dict]:
    """Openverse photographs under any CC licence for ``query`` (``n`` at most, one page)."""
    params = {"q": query, "license_type": "all-cc", "category": "photograph",
              "page_size": str(min(n, OPENVERSE_PAGE_MAX)), "mature": "false"}
    data = _get_json(http, OPENVERSE + "?" + urllib.parse.urlencode(params))
    out = []
    for r in data.get("results") or []:
        if not r.get("url"):
            continue
        out.append({"source": "openverse", "id": f"ov_{r.get('id')}", "url": r["url"], "thumb": r.get("thumbnail"),
                    "title": r.get("title"), "creator": r.get("creator"), "creator_url": r.get("creator_url"),
                    "licence": f"CC {str(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip(),
                    "licence_url": r.get("license_url"), "landing_url": r.get("foreign_landing_url"),
                    "provider": r.get("provider"), "width": r.get("width"), "height": r.get("height"),
                    "query": query})
    return out


def commons_search(query: str, n: int, http: Callable[[str], bytes]) -> list[dict]:
    """Wikimedia Commons files for ``query`` (``n`` at most) with their licence from the file's metadata."""
    params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": "6",
              "gsrsearch": f"{query} filetype:bitmap",
              "gsrlimit": str(min(n, 50)), "prop": "imageinfo", "iiprop": "url|size|extmetadata",
              "iiurlwidth": "1280"}
    data = _get_json(http, COMMONS + "?" + urllib.parse.urlencode(params))
    if not isinstance(data, dict) or "error" in data:
        raise RuntimeError(f"Commons answered: {json.dumps(data)[:240]}")    # pod run 130756: 0 results, no reason
    out = []
    for page in ((data.get("query") or {}).get("pages") or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        url = info.get("thumburl") or info.get("url")
        if not url or not re.search(r"\.(jpe?g|png|webp)$", str(info.get("url") or ""), re.I):
            continue

        def m(key):
            return re.sub(r"<[^>]+>", "", str((meta.get(key) or {}).get("value") or "")).strip() or None
        out.append({"source": "commons", "id": f"wc_{page.get('pageid')}", "url": url, "thumb": info.get("thumburl"),
                    "title": page.get("title"), "creator": m("Artist"), "creator_url": None,
                    "licence": m("LicenseShortName"), "licence_url": m("LicenseUrl"),
                    "landing_url": info.get("descriptionurl"), "provider": "wikimedia",
                    "width": info.get("width"), "height": info.get("height"), "query": query})
    return out


def big_enough(c: dict) -> bool:
    try:
        return max(int(c.get("width") or 0), int(c.get("height") or 0)) >= MIN_SIDE_PX
    except (TypeError, ValueError):
        return False


def select(cands: list[dict], scores: dict, k: int = K_REFERENCES) -> list[dict]:
    """The reference set (pure): ``scores[id]`` = ``{"space": p, "negative": p, "style": s, "quality": q, "vec":
    [...]}`` (``score_images``). A photo whose best negative is more likely than the space is out; the rest rank by
    ``style + quality``; a photo within ``DUPLICATE_COS`` of a kept one is out. Each kept record gets its scores."""
    rows = []
    for c in cands:
        s = scores.get(c["id"])
        if not s or s.get("space") is None or s["space"] < s.get("negative", 0.0):
            continue
        rows.append((float(s.get("style", 0.0)) + float(s.get("quality", 0.0)), c, s))
    rows.sort(key=lambda r: (-r[0], r[1]["id"]))
    kept: list[tuple[dict, dict]] = []
    for _score, c, s in rows:
        vec = s.get("vec")
        if vec is not None and any(_cos(vec, ks.get("vec")) >= DUPLICATE_COS for _kc, ks in kept):
            continue
        kept.append((c, s))
        if len(kept) >= k:
            break
    return [dict(c, scores={k2: round(float(v), 4) for k2, v in s.items() if k2 != "vec"}) for c, s in kept]


def _cos(a, b) -> float:
    if a is None or b is None:
        return 0.0
    num = sum(x * y for x, y in zip(a, b))
    da = sum(x * x for x in a) ** 0.5
    db = sum(y * y for y in b) ** 0.5
    return num / (da * db) if da and db else 0.0


def score_images(paths: dict, space: str, family: Optional[str], device: Optional[str] = None,
                 model_id: Optional[str] = None) -> dict:
    """``{id: {"space", "negative", "style", "quality", "vec"}}`` of downloaded photos (``paths``: id -> file) with
    ``EMBED_MODEL`` (SigLIP 2, sigmoid probabilities of text prompts; ``vec`` the normalised image embedding). Pod
    only (torch, transformers)."""
    import torch
    from transformers import AutoModel, AutoProcessor

    words, interior = SPACES[space]
    fam = " ".join(FAMILY_WORDS.get(str(family or "").lower(), ())[:1])
    texts = [f"a photo of a furnished {words[0]}", *NEGATIVES, f"a {fam} style {words[0]}".replace("  ", " "),
             QUALITY_TEXT if interior else QUALITY_TEXT_OUTDOOR]
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model_id = model_id or (EMBED_MODEL if device == "cuda" else EMBED_MODEL_CPU)
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModel.from_pretrained(model_id, torch_dtype=dtype).to(device).eval()
    proc = AutoProcessor.from_pretrained(model_id)
    out = {}
    with torch.no_grad():
        tin = proc(text=texts, padding="max_length", max_length=64, return_tensors="pt").to(device)
        tvec = _features(model.get_text_features(**tin))
        tvec = tvec / tvec.norm(dim=-1, keepdim=True)
        for pid, path in paths.items():
            try:
                img = open_photo(path)
            except Exception:  # noqa: BLE001 - a broken download is no reference
                continue
            iin = proc(images=[img], return_tensors="pt").to(device)
            ivec = _features(model.get_image_features(**iin))
            ivec = ivec / ivec.norm(dim=-1, keepdim=True)
            logits = (ivec @ tvec.T) * model.logit_scale.exp() + model.logit_bias
            p = torch.sigmoid(logits)[0].float().tolist()
            out[pid] = {"space": p[0], "negative": max(p[1:1 + len(NEGATIVES)]), "style": p[-2], "quality": p[-1],
                        "vec": [round(v, 5) for v in ivec[0].float().tolist()]}
    return out


def _features(out):
    """The embedding tensor of a ``get_*_features`` call: transformers 4 returns the tensor, transformers 5 an output
    object with ``pooler_output`` (pod job 145214: "'BaseModelOutputWithPooling' object has no attribute 'norm'")."""
    for name in ("pooler_output", "image_embeds", "text_embeds"):
        val = getattr(out, name, None)
        if val is not None and not isinstance(out, (list, tuple)) and hasattr(val, "norm"):
            return val
    return out


def set_dir(root, space: str, family: Optional[str]) -> Path:
    return Path(root) / space / re.sub(r"[^a-z0-9]+", "_", str(family or "any").lower())


def fetch_set(space: str, family: Optional[str], root, *, http: Callable[[str], bytes] = default_http,
              scorer: Callable = score_images, k: int = K_REFERENCES, refresh: bool = False) -> dict:
    """The reference set of ``space`` x ``family`` under ``root`` (module docstring): ``manifest.json`` ``{"space",
    "family", "queries", "embed_model", "photos": [...], "searched", "scored", "errors"}``; reused when it exists
    (``refresh`` False)."""
    folder = set_dir(root, space, family)
    man_path = folder / "manifest.json"
    if man_path.is_file() and not refresh:
        old = json.loads(man_path.read_text(encoding="utf-8"))
        if old.get("photos"):
            return old                  # pod run 123917: a set with no photo is fetched again, never reused
    folder.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    cands: list[dict] = []
    qs = queries(space, family)
    per = max(10, CANDIDATES // max(1, len(qs)))
    import time

    def run(q):
        for search in (openverse_search, commons_search):
            try:
                found = search(q, per, http)
                cands.extend(found)
                searched.append(f"{search.__name__}({q!r}): {len(found)}")
            except Exception as exc:  # noqa: BLE001 - one source down: the other one
                errors.append(f"{search.__name__}({q!r}): {type(exc).__name__}: {str(exc)[:200]}")
            if gap:
                time.sleep(gap)
    searched: list[str] = []
    gap = REQUEST_GAP_S if http is default_http else 0.0
    for q in qs:
        run(q)
    if sum(1 for c in cands if big_enough(c)) < 2 * k:
        for q in broad_queries(space, family):
            if q not in qs:
                run(q)
                qs.append(q)
    seen, unique = set(), []
    for c in cands:
        if c["url"] in seen or not big_enough(c):
            continue
        seen.add(c["url"])
        unique.append(c)
    unique = unique[:CANDIDATES]
    raw = folder / "candidates"
    raw.mkdir(exist_ok=True)
    paths = {}
    for c in unique:
        try:
            data = http(c["thumb"] or c["url"]) if c.get("thumb") and c["source"] == "commons" else http(c["url"])
        except Exception as exc:  # noqa: BLE001
            errors.append(f"download {c['id']}: {type(exc).__name__}")
            continue
        ext = ".png" if data[:4] == b"\x89PNG" else ".jpg"
        p = raw / f"{c['id']}{ext}"
        p.write_bytes(data)
        c["sha256"] = hashlib.sha256(data).hexdigest()
        paths[c["id"]] = p
    scores = scorer(paths, space, family) if paths else {}
    kept = select([c for c in unique if c["id"] in paths], scores, k)
    for c in kept:
        src = paths[c["id"]]
        dst = folder / f"{c['id']}{src.suffix}"
        dst.write_bytes(src.read_bytes())
        c["file"] = dst.name
    for p in raw.iterdir():                       # only the kept photos stay on the volume
        p.unlink()
    raw.rmdir()
    man = {"space": space, "family": family, "queries": qs, "embed_model": EMBED_MODEL, "photos": kept,
           "searched": len(cands), "scored": len(scores), "errors": errors[:20], "searches": searched}
    man_path.write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
    return man


def attribution_lines(manifests: list[dict]) -> list[str]:
    """``ATTRIBUTION.md`` lines of the reference photos (used as AI guidance only, never rendered)."""
    out = []
    for man in manifests:
        for p in man.get("photos") or []:
            out.append(f"- \"{p.get('title') or p['id']}\" by {p.get('creator') or 'unknown'} ({p.get('provider')}), "
                       f"{p.get('licence') or 'licence unknown'} ({p.get('licence_url') or '-'}), "
                       f"{p.get('landing_url') or p['url']}: style reference for {man['space']} / {man['family']} "
                       f"(seen by the AI only; not rendered, not changed)")
    return out


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="python -m wenart.style.references")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch", help="gather the reference sets of spaces x families (pod: open internet, GPU)")
    f.add_argument("--spaces", nargs="+", required=True, choices=sorted(SPACES))
    f.add_argument("--families", nargs="+", required=True)
    f.add_argument("--root", default="/workspace/references")
    f.add_argument("--k", type=int, default=K_REFERENCES)
    f.add_argument("--refresh", action="store_true")
    pf = sub.add_parser("prefetch", help="the reference sets of every space in the style family of each project's "
                                         "brief (pod setup, before the servers: the GPU is free)")
    pf.add_argument("--projects", nargs="+", required=True, help="project folders or names under projects/")
    pf.add_argument("--root", default="/workspace/references")
    pf.add_argument("--k", type=int, default=K_REFERENCES)
    cd = sub.add_parser("candidates", help="PD12M caption search -> the best photos per space for the session's "
                                           "choice (pod: Hub, the dataset's bucket, GPU)")
    cd.add_argument("--families", nargs="+", default=["scandinavian"])
    cd.add_argument("--per-space", type=int, default=30)
    cd.add_argument("--root", default="/workspace/references/candidates")
    cd.add_argument("--out", required=True)
    cd.add_argument("--shards", type=int, default=PD12M_SHARDS, help="the first N metadata shards")
    cd.add_argument("--spaces", nargs="*", default=None, help="only these spaces (default: every space)")
    cd.add_argument("--source", choices=SOURCES, default="pexels", help="pexels (styled homes) or pd12m")
    sc = sub.add_parser("score", help="the final renders' similarity to their spaces' reference sets (pod, GPU)")
    sc.add_argument("--project-out", required=True, help="outputs/<p>")
    sc.add_argument("--project", required=True, help="the project (its brief's style family)")
    sc.add_argument("--root", default="/workspace/references")
    sc.add_argument("--out", required=True)
    ex = sub.add_parser("export", help="the sets' manifests, recipes and small copies of the photos for the results")
    ex.add_argument("--root", default="/workspace/references")
    ex.add_argument("--out", required=True)
    ex.add_argument("--size", type=int, default=EXPORT_SIDE_PX)
    a = ap.parse_args(argv)
    if a.cmd == "candidates":
        for fam in a.families:
            counts = candidate_sets(fam, a.root, a.out, a.per_space, spaces=a.spaces or None,
                                    shards=list(range(a.shards)), source=a.source)
            print(f"references candidates {fam}: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
        return 0
    if a.cmd == "score":
        res = style_scores(final_views(a.project_out), a.root, brief_family(a.project))
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
        print(f"style scores: mean similarity {res['mean']} over {len(res['views'])} view(s) -> {a.out}")
        return 0
    if a.cmd == "export":
        n = export(a.root, a.out, a.size)
        print(f"references export: {n} photo(s) -> {a.out}")
        return 0
    if a.cmd == "prefetch":
        import shutil
        import time

        seeded = 0
        if REPO_SETS.is_dir():                    # the committed sets first: no internet needed for them
            for man in sorted(REPO_SETS.glob("*/*/manifest.json")):
                dst = Path(a.root) / man.parent.parent.name / man.parent.name
                old = dst / "manifest.json"
                # 27 Oct 2026: the volume's set gives way unless it holds the committed photos (a new pick reaches
                # the pod; its recipe is read again: recipe_read.set_key)
                if old.is_file() and photo_ids(json.loads(old.read_text(encoding="utf-8"))) == \
                        photo_ids(json.loads(man.read_text(encoding="utf-8"))):
                    continue
                if old.is_file():
                    old.unlink()
                shutil.copytree(man.parent, dst, dirs_exist_ok=True)
                seeded += 1
        print(f"references: {seeded} committed set(s) copied to {a.root}")
        t0 = time.monotonic()
        dead = 0
        pairs = []
        for name in " ".join(a.projects).replace(",", " ").split():
            fam = brief_family(name)
            pairs += [(space, fam) for space in SPACES if (space, fam) not in pairs]
            print(f"references: project {name}: style family {fam!r}")
        failed = 0
        for space, fam in pairs:
            if time.monotonic() - t0 > PREFETCH_BUDGET_S or dead >= DEAD_SETS:
                print(f"references {space}/{fam}: skipped (" + ("the prefetch's time is up" if dead < DEAD_SETS else
                      f"the first {DEAD_SETS} sets found nothing: the sources are unreachable from here") + ")")
                continue
            try:
                man = prefetch_set(space, fam, a.root, k=a.k)
                dead = dead + 1 if not man.get("searched") and not man.get("photos") else 0
                # run 160846: a committed set's manifest has no search counts (KeyError 'searched' on 10 sets)
                errors = man.get("errors") or []
                print(f"references {space}/{fam}: {len(man.get('photos') or [])} kept of {man.get('searched', 0)} found "
                      f"({len(errors)} errors)" + (f"; first error: {errors[0]}" if errors else ""))
            except Exception as exc:  # noqa: BLE001 - one set down: the others, the built-in recipe for it
                failed += 1
                print(f"references {space}/{fam}: failed ({type(exc).__name__}: {str(exc)[:160]})")
        return 1 if failed == len(pairs) and pairs else 0
    for space in a.spaces:
        for fam in a.families:
            man = fetch_set(space, fam, a.root, k=a.k, refresh=a.refresh)
            print(f"references {space}/{fam}: {len(man['photos'])} kept of {man['searched']} found "
                  f"({len(man['errors'])} errors)")
    return 0


# 27 Oct 2026 (user: "find the photos yourself and put it into the pod"): the cloud session reaches no photo host and
# the pod got nothing from Openverse (timeouts) or Commons; PD12M (Spawning/PD12M on the Hub: 12.4 M public-domain and
# CC0 photos with captions, CDLA-Permissive-2.0 metadata, images on the dataset's own S3 bucket) is searched by caption
PD12M_REPO = "Spawning/PD12M"
PD12M_SHARDS = 125
CAPTION_SPACES: dict[str, str] = {
    "living": r"\b(living room|lounge area|sitting room)\b",
    "dining": r"\bdining (room|area)\b",
    "kitchen": r"\bkitchen\b",
    "bedroom": r"\bbedroom\b",
    "child": r"\b(children|child|kids?)['’]?s? ?(bed)?room\b|\bnursery\b",
    "bathroom": r"\bbathroom\b",
    "office": r"\b(home office|study room|workspace)\b",
    "hall": r"\b(hallway|entryway|foyer|entrance hall)\b",
    "dressing": r"\b(walk-in closet|dressing room)\b",
    "veranda": r"\b(porch|veranda|verandah)\b",
    "terrace": r"\b(terrace|patio)\b",
    "balcony": r"\bbalcony\b",
    "garden": r"\b(garden|backyard)\b.*\b(house|home|villa)\b|\b(house|home|villa)\b.*\b(garden|backyard)\b",
}
# 27 Oct 2026 (FAMILY_CAPTION): the words that drop a caption for every family (not a photo of a home), and the period
# words that drop it unless the family's rooms carry them (a classic, rustic or mediterranean room is "antique")
EXCLUDE_WORDS = ("painting", "painted", "drawing", "illustration", "sketch", "engraving", "lithograph", "etching",
                 "poster", "map", "blueprint", "floor plan", "black and white", "black-and-white", "monochrome",
                 "sepia", "old photograph", "museum", "exhibit", "cartoon", "render", "rendering", "3d", "model of",
                 "miniature", "dollhouse", "abandoned", "ruins?", "derelict", "construction site", "church",
                 "cathedral", "palace", "castle")
PERIOD_WORDS = ("vintage", "historic", "historical", "antique")
HOUSE_WORDS = ("modern", "contemporary", "white")     # a facade's words when no family is known (as before)
STOREY_WORDS = ("two-story", "single-story")           # a facade's words in every family
HOUSE_NOUNS = ("house", "home", "villa")


def _family_key(family: Optional[str]) -> str:
    return str(family or "").lower()


def caption_exclude(family: Optional[str] = None) -> str:
    """The caption filter of a family (pure): ``EXCLUDE_WORDS`` and the ``PERIOD_WORDS`` its rooms do not carry
    (``FAMILY_CAPTION`` ``period``); no family or a light one: every period word, as before."""
    allow = set(FAMILY_CAPTION.get(_family_key(family), {}).get("period", ()))
    return r"\b(" + "|".join(EXCLUDE_WORDS + tuple(w for w in PERIOD_WORDS if w not in allow)) + r")\b"


def facade_pattern(family: Optional[str] = None) -> str:
    """The facade's caption pattern of a family (pure): one of its house words (``STOREY_WORDS``, its own words of
    ``FAMILY_WORDS``, ``FAMILY_CAPTION`` ``house``) before a house noun (``HOUSE_NOUNS`` and its ``buildings``), or a
    house "exterior"; no family: the modern, contemporary or white house, as before."""
    key = _family_key(family)
    voc = FAMILY_CAPTION.get(key)
    words = (STOREY_WORDS + FAMILY_WORDS.get(key, ()) + voc["house"]) if voc else HOUSE_WORDS + STOREY_WORDS
    nouns = HOUSE_NOUNS + (voc["buildings"] if voc else ())
    ext = ("house", "villa") + (voc["buildings"] if voc else ())

    def alt(ws):
        return "|".join(re.escape(w) for w in dict.fromkeys(ws))
    return rf"\b({alt(words)}) ({alt(nouns)})\b|\b({alt(ext)}) exterior\b"


CAPTION_SPACES["facade"] = facade_pattern(None)
CAPTION_EXCLUDE = caption_exclude(None)


def caption_spaces(family: Optional[str] = None) -> dict[str, str]:
    """``CAPTION_SPACES`` with the family's facade pattern (``facade_pattern``)."""
    return dict(CAPTION_SPACES, facade=facade_pattern(family))


def caption_points(family: Optional[str] = None) -> Callable[[str], int]:
    """``text -> points`` of a family's caption ranking (pure): ``FAMILY_WORD_POINTS`` for each of its own words
    (``FAMILY_WORDS``), one for each of its look words (``FAMILY_CAPTION``) and of ``QUALITY_WORDS``; each a whole
    word, a plural "s" allowed ("light" is not in "bright", "plant" is in "plants"). No family: the quality words."""
    key = _family_key(family)
    own = tuple(w.lower() for w in FAMILY_WORDS.get(key, ()))
    look = tuple(w for w in dict.fromkeys(FAMILY_CAPTION.get(key, {}).get("look", ()) + QUALITY_WORDS) if w not in own)

    def rx(words):
        return [re.compile(rf"\b{re.escape(w)}s?\b") for w in words]
    own_rx, look_rx = rx(own), rx(look)

    def points(text: str) -> int:
        return (FAMILY_WORD_POINTS * sum(1 for p in own_rx if p.search(text))
                + sum(1 for p in look_rx if p.search(text)))
    return points


CAPTION_KEEP = 400            # candidates kept per space from the captions (style words first)
MIN_PHOTO_SIDE_PX = 1000


def caption_hits(rows, family: Optional[str], spaces=None) -> dict:
    """``{space: [row, ...]}`` of PD12M rows (``id``, ``url``, ``caption``, ``width``, ``height``, ``license``,
    ``source``) whose caption names the space (``caption_spaces``) and none of the family's ``caption_exclude``, at
    least ``MIN_PHOTO_SIDE_PX`` wide or high; each row gets ``style_hits`` (``caption_points``: the family's own words,
    its look words, the quality words) (pure)."""
    points = caption_points(family)
    rx = {k: re.compile(v) for k, v in caption_spaces(family).items() if spaces is None or k in spaces}
    excl = re.compile(caption_exclude(family))
    out: dict = {k: [] for k in rx}
    for r in rows:
        cap = str(r.get("caption") or "").lower()
        if not cap or excl.search(cap):
            continue
        try:
            if max(int(r.get("width") or 0), int(r.get("height") or 0)) < MIN_PHOTO_SIDE_PX:
                continue
        except (TypeError, ValueError):
            continue
        for space, pat in rx.items():
            if space == "bedroom" and rx.get("child") is not None and rx["child"].search(cap):
                continue
            if pat.search(cap):
                out[space].append(dict(r, style_hits=points(cap)))
    return out


def merge_hits(acc: dict, new: dict, keep: int = CAPTION_KEEP) -> dict:
    """The best ``keep`` rows per space of two ``caption_hits`` results (style hits, then the larger photo)."""
    for space, rows in new.items():
        both = acc.get(space, []) + rows
        both.sort(key=lambda r: (-int(r.get("style_hits") or 0), -max(int(r.get("width") or 0),
                                                                       int(r.get("height") or 0)), str(r.get("id"))))
        acc[space] = both[:keep]
    return acc


def pd12m_rows(path) -> list:
    """The rows of one PD12M metadata shard (pyarrow; pod only)."""
    import pyarrow.parquet as pq

    cols = ["id", "url", "caption", "width", "height", "license", "source"]
    return pq.read_table(path, columns=cols).to_pylist()


def pd12m_candidates(family: Optional[str], spaces=None, shards: Optional[list] = None) -> dict:
    """The caption hits of every PD12M shard (``shards``: shard numbers, default all), the shards fetched one by one
    from the Hub (``huggingface_hub``) and deleted after reading."""
    from huggingface_hub import hf_hub_download

    acc: dict = {}
    for i in shards if shards is not None else range(PD12M_SHARDS):
        path = hf_hub_download(PD12M_REPO, f"metadata/pd12m.{i:03d}.parquet", repo_type="dataset")
        acc = merge_hits(acc, caption_hits(pd12m_rows(path), family, spaces))
        try:
            Path(path).unlink()
        except OSError:
            pass
    return acc


# 27 Oct 2026 (user: "find some better photos of the rooms, there should be some more stylish photos online"): PD12M's
# public-domain rooms are mostly museums, hotels and plain homes, so the recipes read from them name shelves and plants
# but no rug, curtains or lamps. Pexels holds the styled homes of interior photography; CaptionEmporium/pexels-568k-
# internvl2 on the Hub lists 567,573 Pexels photos with their title, tags, a detailed InternVL2 caption (CC BY-SA 4.0)
# and the image's address on images.pexels.com (Pexels License: free to use, no attribution required, no resale of
# unaltered copies, https://www.pexels.com/license/). The space is matched on the title and tags (the long caption
# names neighbouring rooms too); the photos whose captions name the most decor layers rank first (``LAYER_WORDS``):
# a styled room, not an empty one.
PEXELS_REPO = "CaptionEmporium/pexels-568k-internvl2"
PEXELS_FILE = "train.jsonl.gz"
PEXELS_LICENCE = "Pexels License (free to use, no attribution required)"
PEXELS_LICENCE_URL = "https://www.pexels.com/license/"
PEXELS_WIDTH_PX = 1600
LAYER_WORDS = ("rug", "carpet", "curtain", "drape", "cushion", "pillow", "throw", "blanket", "plant", "vase", "flower",
               "lamp", "pendant", "chandelier", "artwork", "framed", "picture", "mirror", "candle", "basket", "books",
               "shelf", "shelves", "coffee table", "side table", "armchair", "towel", "bedding", "duvet", "lantern",
               "planter", "string lights", "pergola", "deck", "wicker")
PEOPLE_WORDS = r"\b(woman|women|man|men|people|person|girl|boy|couple|family|lady|guy|model|portrait|selfie)\b"
SOURCES = ("pd12m", "pexels")


def pexels_url(url: str, width: int = PEXELS_WIDTH_PX) -> str:
    """A Pexels image address resized to ``width`` px (the CDN's ``w`` parameter; pure)."""
    return f"{str(url).split('?')[0]}?auto=compress&cs=tinysrgb&w={int(width)}"


def pexels_row(rec: dict) -> Optional[dict]:
    """One row of the Pexels caption list as a candidate row (pure): ``id``, ``url`` (resized), ``url_full``,
    ``caption`` (title and tags: the space is matched here), ``detail`` (the InternVL2 caption: the layers and the
    style words), ``width``, ``height``, ``license``, ``source``, ``landing_url``; None without an image address."""
    url = rec.get("url")
    if not url or (rec.get("type") or "photo") != "photo":
        return None
    title = str(rec.get("title") or rec.get("alt") or "")
    tags = rec.get("tags")
    tags = ", ".join(tags) if isinstance(tags, list) else str(tags or "")
    slug = str(rec.get("slug") or "")
    return {"id": rec.get("id"), "url": pexels_url(url), "url_full": url, "caption": f"{title}. {tags}".strip(),
            "detail": str(rec.get("internvl2_caption") or rec.get("cogvlm_caption") or rec.get("description") or ""),
            "width": rec.get("width"), "height": rec.get("height"), "license": PEXELS_LICENCE_URL, "source": "pexels",
            "landing_url": f"https://www.pexels.com/photo/{slug + '-' if slug else ''}{rec.get('id')}/"}


def pexels_hits(rows, family: Optional[str], spaces=None) -> dict:
    """``{space: [row, ...]}`` of Pexels rows (``pexels_row``) whose title and tags name the space and none of
    the family's ``caption_exclude`` or ``PEOPLE_WORDS``, at least ``MIN_PHOTO_SIDE_PX`` wide or high; ``style_hits``
    = the decor layers the detailed caption names (``LAYER_WORDS``) + the family's ``caption_points`` of the title,
    tags and caption (pure)."""
    points = caption_points(family)
    rx = {k: re.compile(v) for k, v in caption_spaces(family).items() if spaces is None or k in spaces}
    excl, people = re.compile(caption_exclude(family)), re.compile(PEOPLE_WORDS)
    out: dict = {k: [] for k in rx}
    for r in rows:
        if not r:
            continue
        text = str(r.get("caption") or "").lower()
        detail = str(r.get("detail") or "").lower()
        if not text or excl.search(text) or people.search(text):
            continue
        try:
            if max(int(r.get("width") or 0), int(r.get("height") or 0)) < MIN_PHOTO_SIDE_PX:
                continue
        except (TypeError, ValueError):
            continue
        for space, pat in rx.items():
            if space == "bedroom" and rx.get("child") is not None and rx["child"].search(text):
                continue
            if pat.search(text):
                every = f"{text} {detail}"
                hits = points(every) + sum(1 for w in LAYER_WORDS if w in detail)
                out[space].append(dict(r, style_hits=hits))
    return out


def pexels_rows(path):
    """The rows of the Pexels caption list (gzip JSON lines; pod only), one at a time."""
    import gzip

    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            try:
                yield pexels_row(json.loads(line))
            except (ValueError, TypeError):
                continue


def pexels_candidates(family: Optional[str], spaces=None, chunk: int = 50000) -> dict:
    """The hits of the whole Pexels caption list (fetched from the Hub, read in chunks of ``chunk`` rows)."""
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(PEXELS_REPO, PEXELS_FILE, repo_type="dataset")
    acc: dict = {}
    buf: list = []
    for row in pexels_rows(path):
        buf.append(row)
        if len(buf) >= chunk:
            acc = merge_hits(acc, pexels_hits(buf, family, spaces))
            buf = []
    return merge_hits(acc, pexels_hits(buf, family, spaces))


def hits_cache(root, family: Optional[str], source: str = "pd12m") -> Path:
    """The cache of a source's caption hits on the volume (PD12M keeps its first name)."""
    fam = re.sub(r"[^a-z0-9]+", "_", str(family or "any").lower())
    return Path(root) / (f"caption_hits_{fam}.json" if source == "pd12m" else f"caption_hits_{source}_{fam}.json")


def candidate_sets(family: Optional[str], root, out, per_space: int = 30, spaces=None, shards=None,
                   http: Callable[[str], bytes] = default_http, scorer: Callable = score_images,
                   hits: Optional[dict] = None, source: str = "pd12m") -> dict:
    """For the session's choice: per space the ``per_space`` best photos of a source's caption hits (``source``:
    ``pd12m``, downloaded from the dataset's bucket, or ``pexels``, from images.pexels.com at ``PEXELS_WIDTH_PX``),
    ranked by ``scorer`` as ``select``, in ``out/<space>/<family>/`` as 512 px copies with a ``manifest.json``
    (``source``, licence, caption, scores). Returns ``{space: kept count}``."""

    if hits is None:
        cache = hits_cache(root, family, source)
        if cache.is_file():
            hits = json.loads(cache.read_text(encoding="utf-8"))
        else:                                       # every space: the cache serves later picks
            hits = pexels_candidates(family, None) if source == "pexels" else pd12m_candidates(family, None, shards)
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(hits, default=str), encoding="utf-8")
    prefix = "px" if source == "pexels" else "pd"
    counts = {}
    # 27 Oct 2026 (job 150744 ran out of time after balcony .. dressing in name order): the spaces every house has
    # first, and only ``spaces`` when given (the cached caption hits hold every space)
    rank = {sp: k for k, sp in enumerate(CANDIDATE_ORDER)}
    for space, rows in sorted(hits.items(), key=lambda kv: (rank.get(kv[0], len(rank)), kv[0])):
        if spaces and space not in spaces:
            continue
        folder = set_dir(root, space, family)
        folder.mkdir(parents=True, exist_ok=True)
        paths, cands = {}, []
        todo = rows[: CANDIDATES * 2]

        def fetch(r):
            p = folder / f"{prefix}_{r['id']}.jpg"
            if not p.is_file():
                data = None
                for url in dict.fromkeys(u for u in (r.get("url"), r.get("url_full")) if u):
                    try:
                        data = http(url)
                        break
                    except Exception:  # noqa: BLE001 - the next address, else no candidate
                        continue
                if not data:
                    return False
                p.write_bytes(data)
            return True
        # 27 Oct 2026 (job 150744: one download after the other, 120 photos of several MB per space): in parallel
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
            got = list(pool.map(fetch, todo))
        for r, ok in zip(todo, got):
            if not ok:
                continue
            pid = f"{prefix}_{r['id']}"
            p = folder / f"{pid}.jpg"
            paths[pid] = p
            pexels = source == "pexels"
            cands.append({"source": source, "id": pid, "url": r["url"], "title": r.get("caption"),
                          "caption": (f"{r.get('caption')} | {str(r.get('detail') or '')[:600]}" if pexels
                                      else r.get("caption")),
                          "creator": None, "provider": r.get("source"),
                          "licence": PEXELS_LICENCE if pexels else "public domain / CC0 (PD12M)",
                          "licence_url": r.get("license"), "landing_url": r.get("landing_url") or r["url"],
                          "width": r.get("width"), "height": r.get("height"), "style_hits": r.get("style_hits"),
                          **({"caption_licence": "CC BY-SA 4.0 (InternVL2 caption, " + PEXELS_REPO + ")"}
                             if pexels else {})})
        scores = scorer(paths, space, family) if paths else {}
        kept = select(cands, scores, per_space)
        dst = set_dir(out, space, family)
        dst.mkdir(parents=True, exist_ok=True)
        for c in kept:
            try:
                img = open_photo(paths[c["id"]])
                img.thumbnail((EXPORT_SIDE_PX, EXPORT_SIDE_PX))
                img.save(dst / f"{c['id']}.jpg", quality=84)
                c["file"] = f"{c['id']}.jpg"
            except Exception:  # noqa: BLE001
                continue
        kept = [c for c in kept if c.get("file")]
        (dst / "manifest.json").write_text(json.dumps({"space": space, "family": family, "source": source,
                                                       "embed_model": EMBED_MODEL, "photos": kept,
                                                       "candidates": len(rows), "scored": len(scores)},
                                                      indent=1, ensure_ascii=False), encoding="utf-8")
        counts[space] = len(kept)
    return counts


EXPORT_SIDE_PX = 512
DOWNLOAD_WORKERS = 16
CANDIDATE_ORDER = ("living", "kitchen", "veranda", "terrace", "bedroom", "bathroom", "dining", "child", "hall",
                   "garden", "facade", "balcony", "dressing")


def export(root, out, size: int = EXPORT_SIDE_PX) -> int:
    """Copy every set's ``manifest.json`` and ``recipe.json`` and its photos at ``size`` px (JPEG) from ``root`` to
    ``out`` (the run's results, for the review); returns the number of photos."""

    n = 0
    for man_path in sorted(Path(root).glob("*/*/manifest.json")):
        folder = man_path.parent
        dst = Path(out) / folder.parent.name / folder.name
        dst.mkdir(parents=True, exist_ok=True)
        for name in ("manifest.json", "recipe.json"):
            if (folder / name).is_file():
                (dst / name).write_bytes((folder / name).read_bytes())
        man = json.loads(man_path.read_text(encoding="utf-8"))
        for p in man.get("photos") or []:
            src = folder / str(p.get("file") or "")
            if not src.is_file():
                continue
            try:
                img = open_photo(src)
                img.thumbnail((size, size))
                img.save(dst / (src.stem + ".jpg"), quality=82)
                n += 1
            except Exception:  # noqa: BLE001 - a broken photo is left out of the copy
                continue
    return n


_EMBEDDER: dict = {}          # device -> (model, processor) of EMBED_MODEL


def embed(paths: list, device: str = "cuda") -> list:
    """Normalised SigLIP 2 image embeddings of ``paths`` (pod only), a list of float lists (None for a broken file)."""
    import torch
    from transformers import AutoModel, AutoProcessor

    # run 160846: style_scores calls this once per set and once per view; the model loads once
    if device not in _EMBEDDER:
        _EMBEDDER[device] = (AutoModel.from_pretrained(EMBED_MODEL, torch_dtype=torch.float16).to(device).eval(),
                             AutoProcessor.from_pretrained(EMBED_MODEL))
    model, proc = _EMBEDDER[device]
    out = []
    with torch.no_grad():
        for p in paths:
            try:
                img = open_photo(p)
            except Exception:  # noqa: BLE001
                out.append(None)
                continue
            v = _features(model.get_image_features(**proc(images=[img], return_tensors="pt").to(device)))
            v = v / v.norm(dim=-1, keepdim=True)
            out.append([float(x) for x in v[0].float().tolist()])
    return out


def style_scores(views: list[dict], root, family: Optional[str], embed_fn=embed) -> dict:
    """27 Oct 2026 (UL42): how close each final render is to the good photos of its space and style (``views``:
    ``{"name", "image", "space"}``): the cosine similarity of its SigLIP 2 embedding to the mean of the reference
    set's (``similarity``, -1..1; real photos of one space and style score about 0.6-0.8 against their own mean) and the
    best single photo (``best``); ``{"views": [...], "mean", "by_space"}``. A view whose space has no set is left
    out with the reason."""
    rows, sets = [], {}
    for v in views:
        space = v.get("space")
        folder = set_dir(root, space, family) if space else None
        man = folder / "manifest.json" if folder else None
        if man is None or not man.is_file():
            rows.append({"view": v["name"], "space": space, "similarity": None, "reason": "no reference set"})
            continue
        if space not in sets:
            photos = json.loads(man.read_text(encoding="utf-8")).get("photos") or []
            vecs = [x for x in embed_fn([folder / p["file"] for p in photos if p.get("file")]) if x]
            sets[space] = vecs
        vecs = sets[space]
        if not vecs:
            rows.append({"view": v["name"], "space": space, "similarity": None, "reason": "no photo in the set"})
            continue
        mine = (embed_fn([v["image"]]) or [None])[0]
        if mine is None:
            rows.append({"view": v["name"], "space": space, "similarity": None, "reason": "render unreadable"})
            continue
        centre = [sum(c) / len(vecs) for c in zip(*vecs)]
        rows.append({"view": v["name"], "space": space, "similarity": round(_cos(mine, centre), 4),
                     "best": round(max(_cos(mine, x) for x in vecs), 4)})
    vals = [r["similarity"] for r in rows if r.get("similarity") is not None]
    by: dict = {}
    for r in rows:
        if r.get("similarity") is not None:
            by.setdefault(r["space"], []).append(r["similarity"])
    return {"views": rows, "mean": round(sum(vals) / len(vals), 4) if vals else None,
            "by_space": {k: round(sum(x) / len(x), 4) for k, x in sorted(by.items())}, "embed_model": EMBED_MODEL,
            "family": family}


def final_views(project_out) -> list[dict]:
    """The final renders of a project (``final/final_manifest.json`` views, else ``final/*_final_preview.jpg``) with
    their reference space (the room's, ``facade`` for an exterior view)."""
    out_dir = Path(project_out)
    building = {}
    for name in ("scene/building_built.json", "building_final.json"):
        if (out_dir / name).is_file():
            building = json.loads((out_dir / name).read_text(encoding="utf-8"))
            break
    rooms = {r.get("id"): r for r in building.get("rooms") or []}
    views = []
    for img in sorted((out_dir / "final").glob("*_final_preview.jpg")):
        name = img.name[: -len("_final_preview.jpg")]
        room_id = next((rid for rid in rooms if rid and name.startswith(f"cam_{rid}_")), None)
        room = rooms.get(room_id) or {}
        space = space_of(room.get("room_type"), room.get("room_subtype")) if room else "facade"
        views.append({"name": name, "image": img, "space": space})
    return views


AUTO_ROOT = "candidates"       # under the reference root: the full-size downloads of the automatic sets


def prefetch_set(space: str, family: Optional[str], root, k: int = K_REFERENCES, *, auto=None, search=None) -> dict:
    """The reference set of ``space`` and ``family`` for a run (27 Oct 2026, user: "all the solutions must be general";
    the session hand-picked sets for one family only, and Openverse and Commons answer no pod): a set on the volume
    with photos (committed, ``REPO_SETS``, or kept from an earlier run) as it is; else the automatic set of the Pexels
    caption list (``candidate_sets`` with ``per_space`` ``k``: the space on the title and tags, ranked by the decor
    layers and SigLIP 2, written to the set's folder with ``picked_by`` automatic); else the Openverse and Commons search
    (``fetch_set``). ``auto`` and ``search``: the two sources (tests)."""
    folder = set_dir(root, space, family)
    man_path = folder / "manifest.json"
    if man_path.is_file():
        try:
            old = json.loads(man_path.read_text(encoding="utf-8"))
        except ValueError:
            old = {}
        if old.get("photos"):
            return dict(old, searched=old.get("searched", len(old["photos"])), errors=old.get("errors") or [])
    errors: list = []
    try:
        counts = (auto or candidate_sets)(family, Path(root) / AUTO_ROOT, root, k, spaces=[space], source="pexels")
        if counts.get(space) and man_path.is_file():
            man = json.loads(man_path.read_text(encoding="utf-8"))
            man.update(picked_by="automatic (Pexels caption search, decor layers, SigLIP 2 ranking)",
                       searched=man.get("candidates") or len(man.get("photos") or []), errors=[])
            man_path.write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")
            return man
        errors.append(f"pexels: no photo of {space} kept")
    except Exception as exc:  # noqa: BLE001 - the next source; the reason is kept
        errors.append(f"pexels: {type(exc).__name__}: {str(exc)[:160]}")
    man = (search or fetch_set)(space, family, root, k=k)
    return dict(man, errors=errors + list(man.get("errors") or []))


def open_photo(path):
    """A photo as RGB, upright (27 Oct 2026, job 150744: a camera's rotation tag left photos on their side in the
    512 px copies, which keep no tag): ``ImageOps.exif_transpose`` first."""
    from PIL import Image, ImageOps

    img = Image.open(path)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:  # noqa: BLE001 - a broken tag: the photo as stored
        pass
    return img.convert("RGB")


def photo_ids(manifest: dict) -> list:
    """The sorted photo ids of a set's manifest (pure)."""
    return sorted(str(p.get("id")) for p in (manifest or {}).get("photos") or [])


def contact_sheet(folder, out_path, cols: int = 6, side: int = 256, title: str = "",
                  picked: Optional[set] = None) -> int:
    """A numbered contact sheet of a set's photos (``folder/manifest.json`` order): ``cols`` per row, ``side`` px
    tiles, the 1-based number on each tile (green for the ``picked`` ids); returns the number of tiles (pure but for
    the files)."""
    from PIL import Image, ImageDraw

    folder = Path(folder)
    photos = json.loads((folder / "manifest.json").read_text(encoding="utf-8")).get("photos") or []
    tiles = [(i + 1, p) for i, p in enumerate(photos) if (folder / str(p.get("file") or "")).is_file()]
    if not tiles:
        return 0
    rows = (len(tiles) + cols - 1) // cols
    head = 28 if title else 0
    sheet = Image.new("RGB", (cols * side, rows * side + head), (24, 24, 24))
    draw = ImageDraw.Draw(sheet)
    if title:
        draw.text((8, 8), title, fill=(235, 235, 235))
    for k, (n, p) in enumerate(tiles):
        img = open_photo(folder / p["file"])
        img.thumbnail((side - 6, side - 6))
        x, y = (k % cols) * side, (k // cols) * side + head
        sheet.paste(img, (x + (side - img.width) // 2, y + (side - img.height) // 2))
        mark = picked is not None and p.get("id") in picked
        draw.rectangle([x + 3, y + 3, x + 33, y + 21], fill=(30, 140, 60) if mark else (0, 0, 0))
        draw.text((x + 7, y + 6), str(n), fill=(255, 255, 255))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=85)
    return len(tiles)


def brief_family(project) -> Optional[str]:
    """The style family of a project's brief (``projects/<name>`` or a folder): the family the style stage writes to
    style.json (``profile.profiles_from_brief`` -> ``fit.style_family_of``), None without style words."""
    from wenart.brief import load_brief
    from wenart.furniture.fit import style_family_of
    from wenart.style import profile as SPF

    folder = Path(project) if Path(project).is_dir() else Path("projects") / str(project)
    brief = load_brief(folder)["values"]
    try:
        return style_family_of(SPF.profiles_from_brief(brief))[0]
    except Exception:  # noqa: BLE001 - no style words: no family
        return None


if __name__ == "__main__":
    raise SystemExit(main())
