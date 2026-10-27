"""Reading the reference photos into recipes (27 Oct 2026, lesson UL42): the vision-model side of
``wenart.style.recipe`` (kept apart so the decor stage, which only reads recipes, does not depend on the model client).

- ``read_photo(model, path, ...)``: one reference photo through the vision model's ``critic`` call (temperature 0,
  ``recipe.photo_schema``).
- ``recipe_for(model, manifest, root)``: the recipe of a reference set, read once per photo set (``set_key``) and
  cached beside its photos (``recipe.json``).
- ``recipes_for(spaces, family, root, model)``: a project's ``{space: recipe}``: the photos' recipe where its set
  exists, else ``recipe.default_recipe``.
- ``project_spaces(building)``: the reference spaces of a building.
- CLI ``python -m wenart.style.recipe_read build <building> --style style.json --out recipes.json [--server URL
  --model ID] [--root /workspace/references]``.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from wenart.style.recipe import SYSTEM, aggregate, default_recipe, photo_prompt, photo_schema


def read_photo(model, path, space_words: str, family: Optional[str], interior: bool, *, call_id: str = "") -> dict:
    """One reference photo's answer through the vision model's ``critic`` call (strict schema) or ``{"error"}``."""
    from wenart.agent.model import user_message

    reply = model.critic([{"role": "system", "content": SYSTEM},
                          user_message(photo_prompt(space_words, family, interior), [Path(path)], [None])],
                         photo_schema(interior), call_id=call_id)
    if reply.data is None:
        return {"error": "; ".join(reply.errors[:2]) or "no answer"}
    return dict(reply.data)


def set_key(manifest: dict) -> str:
    """The cache key of a reference set: its photos' hashes (a re-fetched set with the same photos keeps its recipe)."""
    blob = json.dumps(sorted(str(p.get("sha256") or p.get("id")) for p in manifest.get("photos") or []))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def recipe_for(model, manifest: dict, root, cache: Optional[Path] = None) -> dict:
    """The recipe of a reference set (``references.fetch_set``'s manifest, its photos under ``root``), read once per
    set and cached in ``cache`` (default: the set's folder, ``recipe.json``) by ``set_key``."""
    from wenart.style import references as RF

    space, family = manifest["space"], manifest.get("family")
    words, interior = RF.SPACES[space]
    folder = RF.set_dir(root, space, family)
    path = Path(cache) if cache else folder / "recipe.json"
    key = set_key(manifest)
    if path.is_file():
        old = json.loads(path.read_text(encoding="utf-8"))
        if old.get("set_key") == key:
            return old
    answers = []
    for i, p in enumerate(manifest.get("photos") or []):
        ans = read_photo(model, folder / p["file"], words[0], family, interior,
                         call_id=f"recipe-{space}-{i + 1}")
        answers.append(dict(ans, photo=p["id"]))
    rec = dict(aggregate(answers, interior), space=space, family=family, set_key=key,
               model=getattr(model, "model", ""), answers=answers)
    path.write_text(json.dumps(rec, indent=1, ensure_ascii=False), encoding="utf-8")
    return rec


def recipes_for(spaces: list[str], family: Optional[str], root, model=None) -> dict:
    """``{space: recipe}`` of a project (``recipes.json``): the photos' recipe where the reference set exists under
    ``root`` (read with ``model`` when not cached; a set without photos or an unreadable one keeps the default)."""
    from wenart.style import references as RF

    out = {}
    for space in spaces:
        rec = None
        man_path = RF.set_dir(root, space, family) / "manifest.json" if root else None
        if man_path is not None and man_path.is_file():
            man = json.loads(man_path.read_text(encoding="utf-8"))
            cached = man_path.parent / "recipe.json"
            if man.get("photos") and (model is not None or cached.is_file()):
                try:
                    rec = recipe_for(model, man, root) if model is not None else json.loads(cached.read_text())
                    rec = dict({k: v for k, v in rec.items() if k != "answers"}, source="photos")
                    if not rec.get("n"):
                        rec = None
                except Exception as exc:  # noqa: BLE001 - one unreadable set keeps the default
                    rec = dict(default_recipe(space), error=f"{type(exc).__name__}: {str(exc)[:160]}")
        out[space] = rec or default_recipe(space)
    return out


def project_spaces(building: dict) -> list[str]:
    """The reference spaces of a building: its rooms' (``references.space_of``) and its outdoor spaces' kinds,
    plus the garden and the facade."""
    from wenart.style import references as RF

    spaces = [RF.space_of(r.get("room_type"), r.get("room_subtype")) for r in building.get("rooms") or []]
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    spaces += [RF.space_of(None, outdoor=o.get("kind") or o.get("label")) for o in site.get("outdoor_spaces") or []]
    spaces += ["garden", "facade"]
    return sorted({s for s in spaces if s})


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="python -m wenart.style.recipe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="the project's recipes.json from the reference sets (pod: the vision server)")
    b.add_argument("building")
    b.add_argument("--style", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--root", default="/workspace/references")
    b.add_argument("--server")
    b.add_argument("--key", default="agent", help="check.yaml model key of the server (the decor's layout key)")
    a = ap.parse_args(argv)
    building = json.loads(Path(a.building).read_text(encoding="utf-8"))
    style = json.loads(Path(a.style).read_text(encoding="utf-8"))
    from wenart.furniture.fit import style_family_of

    family = style_family_of(style)[0]
    model = None
    if a.server:
        from wenart.agent.model import from_check_yaml

        model = from_check_yaml(a.server, a.key)
    recs = recipes_for(project_spaces(building), family, a.root, model)
    Path(a.out).write_text(json.dumps({"family": family, "recipes": recs}, indent=1, ensure_ascii=False),
                           encoding="utf-8")
    for space, r in recs.items():
        print(f"recipe {space}: {r.get('source')} ({r.get('n')} photos): must {', '.join(r.get('must') or [])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
