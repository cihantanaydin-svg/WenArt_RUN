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
K_REFERENCES = 8                # photos kept per space and family
CANDIDATES = 60                 # candidates scored per space and family
MIN_SIDE_PX = 700               # a photo smaller than this both ways is too small to read a room from
DUPLICATE_COS = 0.95            # two photos this similar (image embeddings) are one
EMBED_MODEL = "google/siglip2-so400m-patch14-384"     # Apache-2.0 (checked on the Hub 27 Oct 2026)
NEGATIVES = ("a floor plan or a drawing", "a 3D render or a computer graphic", "a product photo on a white background",
             "a photo of people", "an empty unfurnished room", "a messy cluttered room", "a text document or a sign")
QUALITY_TEXT = "a beautiful professional interior design photo, magazine quality"
QUALITY_TEXT_OUTDOOR = "a beautiful professional architecture and landscape photo, magazine quality"
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


def _get_json(http: Callable[[str], bytes], url: str) -> dict:
    return json.loads(http(url).decode("utf-8"))


def default_http(url: str, timeout: float = 30.0) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:      # noqa: S310 - https only, fixed hosts
        return resp.read()


def openverse_search(query: str, n: int, http: Callable[[str], bytes]) -> list[dict]:
    """Openverse photographs under any CC licence for ``query`` (``n`` at most, one page)."""
    params = {"q": query, "license_type": "all-cc", "category": "photograph", "page_size": str(min(n, 50)),
              "mature": "false"}
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
    params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": "6", "gsrsearch": query,
              "gsrlimit": str(min(n, 50)), "prop": "imageinfo", "iiprop": "url|size|extmetadata",
              "iiurlwidth": "1280"}
    data = _get_json(http, COMMONS + "?" + urllib.parse.urlencode(params))
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


def score_images(paths: dict, space: str, family: Optional[str], device: str = "cuda") -> dict:
    """``{id: {"space", "negative", "style", "quality", "vec"}}`` of downloaded photos (``paths``: id -> file) with
    ``EMBED_MODEL`` (SigLIP 2, sigmoid probabilities of text prompts; ``vec`` the normalised image embedding). Pod
    only (torch, transformers)."""
    import torch
    from PIL import Image
    from transformers import AutoModel, AutoProcessor

    words, interior = SPACES[space]
    fam = " ".join(FAMILY_WORDS.get(str(family or "").lower(), ())[:1])
    texts = [f"a photo of a furnished {words[0]}", *NEGATIVES, f"a {fam} style {words[0]}".replace("  ", " "),
             QUALITY_TEXT if interior else QUALITY_TEXT_OUTDOOR]
    model = AutoModel.from_pretrained(EMBED_MODEL, torch_dtype=torch.float16).to(device).eval()
    proc = AutoProcessor.from_pretrained(EMBED_MODEL)
    out = {}
    with torch.no_grad():
        tin = proc(text=texts, padding="max_length", max_length=64, return_tensors="pt").to(device)
        tvec = model.get_text_features(**tin)
        tvec = tvec / tvec.norm(dim=-1, keepdim=True)
        for pid, path in paths.items():
            try:
                img = Image.open(path).convert("RGB")
            except Exception:  # noqa: BLE001 - a broken download is no reference
                continue
            iin = proc(images=[img], return_tensors="pt").to(device)
            ivec = model.get_image_features(**iin)
            ivec = ivec / ivec.norm(dim=-1, keepdim=True)
            logits = (ivec @ tvec.T) * model.logit_scale.exp() + model.logit_bias
            p = torch.sigmoid(logits)[0].float().tolist()
            out[pid] = {"space": p[0], "negative": max(p[1:1 + len(NEGATIVES)]), "style": p[-2], "quality": p[-1],
                        "vec": [round(v, 5) for v in ivec[0].float().tolist()]}
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
        return json.loads(man_path.read_text(encoding="utf-8"))
    folder.mkdir(parents=True, exist_ok=True)
    errors: list[str] = []
    cands: list[dict] = []
    qs = queries(space, family)
    per = max(10, CANDIDATES // max(1, len(qs)))
    for q in qs:
        for search in (openverse_search, commons_search):
            try:
                cands += search(q, per, http)
            except Exception as exc:  # noqa: BLE001 - one source down: the other one
                errors.append(f"{search.__name__}({q!r}): {type(exc).__name__}: {str(exc)[:120]}")
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
           "searched": len(cands), "scored": len(scores), "errors": errors[:20]}
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
        pairs = []
        for name in " ".join(a.projects).replace(",", " ").split():
            fam = brief_family(name)
            pairs += [(space, fam) for space in SPACES if (space, fam) not in pairs]
            print(f"references: project {name}: style family {fam!r}")
        failed = 0
        for space, fam in pairs:
            try:
                man = fetch_set(space, fam, a.root, k=a.k)
                print(f"references {space}/{fam}: {len(man['photos'])} kept of {man['searched']} found "
                      f"({len(man['errors'])} errors)")
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


EXPORT_SIDE_PX = 512


def export(root, out, size: int = EXPORT_SIDE_PX) -> int:
    """Copy every set's ``manifest.json`` and ``recipe.json`` and its photos at ``size`` px (JPEG) from ``root`` to
    ``out`` (the run's results, for the review); returns the number of photos."""
    from PIL import Image

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
                img = Image.open(src).convert("RGB")
                img.thumbnail((size, size))
                img.save(dst / (src.stem + ".jpg"), quality=82)
                n += 1
            except Exception:  # noqa: BLE001 - a broken photo is left out of the copy
                continue
    return n


def embed(paths: list, device: str = "cuda") -> list:
    """Normalised SigLIP 2 image embeddings of ``paths`` (pod only), a list of float lists (None for a broken file)."""
    import torch
    from PIL import Image
    from transformers import AutoModel, AutoProcessor

    model = AutoModel.from_pretrained(EMBED_MODEL, torch_dtype=torch.float16).to(device).eval()
    proc = AutoProcessor.from_pretrained(EMBED_MODEL)
    out = []
    with torch.no_grad():
        for p in paths:
            try:
                img = Image.open(p).convert("RGB")
            except Exception:  # noqa: BLE001
                out.append(None)
                continue
            v = model.get_image_features(**proc(images=[img], return_tensors="pt").to(device))
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
