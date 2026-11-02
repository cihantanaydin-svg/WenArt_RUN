"""Typical floors' copies (2 Nov 2026, real10 run 20261101-233829-full; user decision of 1 Nov 2026 for real10: one flat
rendered per distinct plan, "the other typical floors are copies").

What: a level that copies a typical floor (``typical_of``, ``wenart/sheets/variants.py``) is furnished as that floor
(``furnish_typical_copies``, pure, run by ``build.prepare_once``) and its furniture and decor objects are built as linked
duplicates of the typical floor's (``copy_furniture``, bpy: object copies sharing the mesh data, raised by the levels'
height difference, ids and names moved to the copy's level, the manifest entries copied with ``typical_copy_of``).

Why: an apartment block's typical floor is read once and copied (real10: L1-L6 copies of L0). The stages furnished each
copy on its own (the model picks varied floor by floor): 1,156 pieces and 1,601 decor items, about 0.6 s each to
build, and the build was still at it after three hours. A linked duplicate costs a few milliseconds and renders the
same; the building as built says what was built.

How: ``build.main`` builds a typical floor's furniture in its own collection (``furniture_<level>`` under the level's
collection) and keeps its manifest entries, summary and scene-check report; a copy level then gets ``copy_furniture``
instead of ``furniture.create_furniture`` (a copy that cannot be made falls back to building its pieces, with a
warning). Pure helpers (``furnish_typical_copies``, ``renamer``, ``copy_entries``, ``copy_summary``) run anywhere.
"""
from __future__ import annotations

import copy as _copy
from typing import Optional



TYPICAL_FURNISHED = ("furniture", "decor")     # the lists a typical floor's copy takes from its typical floor


TYPICAL_KEEP_KEYS = ("evidence", "crop", "typical_copy_of", "attribution", "path", "file", "source_path")


def _renamed(value, rename: dict, tag: str = "", new_tag: str = ""):
    """``value`` with every string equal to a key of ``rename`` replaced, and ``tag`` read as ``new_tag`` inside every
    other string (a group id ``r_L0_mutfak``, a slot ``f_L0_101:top``, a reason); the values under
    ``TYPICAL_KEEP_KEYS`` (the evidence and its crops, file paths, attributions) are kept as they are: they name the
    real source. Dicts and lists walked; pure."""
    if isinstance(value, str):
        if value in rename:
            return rename[value]
        return value.replace(tag, new_tag) if tag and tag in value else value
    if isinstance(value, list):
        return [_renamed(v, rename, tag, new_tag) for v in value]
    if isinstance(value, dict):
        return {k: (v if k in TYPICAL_KEEP_KEYS else _renamed(v, rename, tag, new_tag)) for k, v in value.items()}
    return value


TYPICAL_FURNISH_EACH_MAX = 3   # identical floors (a typical floor and its copies) up to this many are each furnished
STAIR_TYPES = ("stair", "stairs", "staircase")      # kept on an unfurnished copy: the stair is the building's


def unfurnished_copies(building: dict) -> dict[str, str]:
    """``{copy level: typical floor}``: the copies left unfurnished (pure). User rule of 2 Nov 2026 ("for the buildings
    with the same exact floors more than 3 floors, we can skip the furnishing of the each exact floors, only 1 example
    floor furnishing would be enough"): when a typical floor and its copies are more than ``TYPICAL_FURNISH_EACH_MAX``
    identical floors, only the typical floor is furnished; its copies keep their stairs and nothing else."""
    levels = {lv["id"]: lv for lv in building.get("levels") or [] if isinstance(lv, dict) and lv.get("id")}
    groups: dict = {}
    for lid, lv in levels.items():
        base = lv.get("typical_of")
        if base and base in levels and base != lid:
            groups.setdefault(base, []).append(lid)
    return {c: base for base, copies in groups.items() if 1 + len(copies) > TYPICAL_FURNISH_EACH_MAX
            for c in copies}


def furnish_typical_copies(building: dict) -> list[dict]:
    """Every level that is a typical floor's copy (``typical_of``) furnished as its typical floor (in place; pure):
    its furniture and decor are replaced by the typical floor's, with the ids moved to the copy's level (``_<typical>_``
    read as ``_<copy>_``, an id without it gets ``@<copy>``), every reference to the typical floor's rooms, walls,
    openings, pieces and decor moved to the copy's own (``_renamed``: exact ids, and the level token inside group ids,
    slots and reasons; the evidence keeps naming the real source), ``floor_z`` raised by the levels' height difference
    and ``typical_copy_of`` naming the source item. Returns one assumed record per copy.

    2 Nov 2026 (real10 run 20261101-233829-full; user decision of 1 Nov 2026 for real10: one flat rendered per distinct
    plan, "the other typical floors are copies"): the stages furnished each typical floor on its own (the model picks
    varied floor by floor), so the build made 1,156 pieces and 1,601 decor items and was still at it after three hours;
    as copies the build makes the typical floor's pieces once and the copies as linked duplicates (``main``), and the
    building as built says what was built."""
    levels = {lv["id"]: lv for lv in building.get("levels") or [] if isinstance(lv, dict) and lv.get("id")}
    base_of = {lid: lv["typical_of"] for lid, lv in levels.items()
               if lv.get("typical_of") and lv["typical_of"] in levels and lv["typical_of"] != lid}
    if not base_of:
        return []
    all_ids = {e["id"] for v in building.values() if isinstance(v, list) for e in v
               if isinstance(e, dict) and isinstance(e.get("id"), str)}
    records = []
    bare = unfurnished_copies(building)
    for copy_id, base in sorted(base_of.items()):
        if copy_id in bare:
            counts = {}
            for key in TYPICAL_FURNISHED:
                old = building.get(key) or []
                on = [e for e in old if isinstance(e, dict) and e.get("level_id") == copy_id]
                keep = [e for e in on if key == "furniture" and str(e.get("type") or "").lower() in STAIR_TYPES]
                building[key] = [e for e in old if not (isinstance(e, dict) and e.get("level_id") == copy_id)
                                 or e in keep]
                counts[key] = {"was": len(on), "now": len(keep)}
            n = 1 + sum(1 for b in base_of.values() if b == base)
            records.append({"object": f"level_{copy_id}", "field": "furnishing", "value": "none",
                            "kind": "typical_copy", "parent": f"level_{copy_id}", "counts": counts,
                            "reason": (f"{copy_id} is one of {n} identical floors (a copy of the typical floor {base}, "
                                       f"typical_of): only {base} is furnished, as the example floor (user rule of 2 Nov "
                                       f"2026: more than {TYPICAL_FURNISH_EACH_MAX} identical floors, one example floor "
                                       f"furnished); its {counts['furniture']['was']} pieces and "
                                       f"{counts['decor']['was']} decor items are left out, its stairs kept "
                                       f"({counts['furniture']['now']})")})
            continue
        tag, new_tag = f"_{base}_", f"_{copy_id}_"
        dz = float(levels[copy_id].get("elevation") or 0.0) - float(levels[base].get("elevation") or 0.0)
        rename: dict = {}
        for key, items in building.items():
            if key in TYPICAL_FURNISHED or not isinstance(items, list):
                continue
            for e in items:
                if isinstance(e, dict) and e.get("level_id") == base and isinstance(e.get("id"), str):
                    twin = e["id"].replace(tag, new_tag, 1)
                    if twin != e["id"] and twin in all_ids:
                        rename[e["id"]] = twin
        sources = {key: [e for e in building.get(key) or [] if isinstance(e, dict) and e.get("level_id") == base]
                   for key in TYPICAL_FURNISHED}
        for key, items in sources.items():
            for e in items:
                new_id = e["id"].replace(tag, new_tag, 1) if tag in e["id"] else f"{e['id']}@{copy_id}"
                rename[e["id"]] = new_id
        counts = {}
        for key, items in sources.items():
            old = building.get(key) or []
            dropped = [e for e in old if isinstance(e, dict) and e.get("level_id") == copy_id]
            made = []
            for e in items:
                q = _renamed(_copy.deepcopy(e), rename, tag, new_tag)
                q["level_id"] = copy_id
                q["typical_copy_of"] = e["id"]
                if q.get("floor_z") is not None:
                    q["floor_z"] = round(float(q["floor_z"]) + dz, 4)
                made.append(q)
            at = next((i for i, e in enumerate(old) if isinstance(e, dict) and e.get("level_id") == copy_id),
                      len(old))
            kept = [e for e in old if not (isinstance(e, dict) and e.get("level_id") == copy_id)]
            at = sum(1 for e in old[:at] if not (isinstance(e, dict) and e.get("level_id") == copy_id))
            building[key] = kept[:at] + made + kept[at:]
            counts[key] = {"was": len(dropped), "now": len(made)}
        records.append({"object": f"level_{copy_id}", "field": "furnishing", "value": f"as {base}",
                        "kind": "typical_copy", "parent": f"level_{copy_id}",
                        "reason": (f"{copy_id} is a copy of the typical floor {base} (typical_of): furnished as {base} "
                                   f"({counts['furniture']['now']} pieces for the {counts['furniture']['was']} placed "
                                   f"on it, {counts['decor']['now']} decor items for {counts['decor']['was']}; one "
                                   f"flat design per typical floor, the copies built as linked duplicates)"),
                        "counts": counts})
    return records


def renamer(base: str, copy_id: str):
    """``(name_of, id_of)``: an object name and an element id of the typical floor ``base`` moved to ``copy_id`` (pure):
    the level token ``_<base>_`` read as ``_<copy>_``; a name without it gets ``@<copy>`` (an id without it is kept)."""
    tag, new_tag = f"_{base}_", f"_{copy_id}_"

    def name_of(name: str) -> str:
        return name.replace(tag, new_tag) if tag in name else f"{name}@{copy_id}"

    def id_of(value):
        return value.replace(tag, new_tag) if isinstance(value, str) and tag in value else value
    return name_of, id_of


def _raise_z(rec: dict, dz: float) -> None:
    for key in ("center",):
        v = rec.get(key)
        if isinstance(v, list) and len(v) == 3 and isinstance(v[2], (int, float)):
            v[2] = round(float(v[2]) + dz, 5)
    box = rec.get("box3d")
    if isinstance(box, dict):
        _raise_z(box, dz)


def copy_entries(entries: list, name_map: dict, base: str, copy_id: str, dz: float) -> list[dict]:
    """The manifest entries of the typical floor's furniture and decor objects for the copy (pure): only the entries of
    objects that were copied (``name_map``: source name -> copy name), every string with the level token moved
    (``_renamed``; the evidence, files and attributions kept), the 3D centres raised by ``dz``, ``level_id`` the
    copy's and ``typical_copy_of`` the source object."""
    tag, new_tag = f"_{base}_", f"_{copy_id}_"
    out = []
    for e in entries:
        if not isinstance(e, dict) or e.get("name") not in name_map:
            continue
        q = _renamed(_copy.deepcopy(e), {}, tag, new_tag)
        q["name"] = name_map[e["name"]]
        q["level_id"] = copy_id
        q["typical_copy_of"] = e["name"]
        _raise_z(q, dz)
        out.append(q)
    return out


def copy_summary(summary: dict, base: str, copy_id: str, objects: dict) -> dict:
    """The furniture summary of the copy (pure): the typical floor's, its ids moved, ``objects`` the copy's objects,
    the timings left out (they are the source's), ``typical_copy_of`` the typical floor."""
    tag, new_tag = f"_{base}_", f"_{copy_id}_"
    s = {k: v for k, v in summary.items() if k not in ("objects", "slowest")}
    s = _renamed(_copy.deepcopy(s), {}, tag, new_tag)
    s["objects"] = objects
    s["typical_copy_of"] = base
    return s


MODIFIER_OBJECT_ATTRS = ("object", "offset_object", "mirror_object", "start_cap", "end_cap", "curve", "target",
                         "origin")


def copy_furniture(src: dict, level: dict, parent_collection, manifest_objects: list) -> dict:
    """The typical floor's furniture and decor objects (``src``: ``{"level", "collection", "entries", "summary"}``)
    duplicated for the copy ``level`` (bpy): every object of the source collection (nested ones too) copied with its
    data shared, parents and modifier or constraint targets inside the set pointed at the copies, the roots raised by
    the levels' height difference, the string properties (``wenart_id`` ...) moved to the copy's level; the copies go
    in ``furniture_<level>`` under ``parent_collection``. The manifest entries are added; returns ``{"summary",
    "collection", "objects"}``."""
    import bpy
    from mathutils import Matrix

    base = src["level"]["id"]
    copy_id = level["id"]
    dz = float(level.get("elevation") or 0.0) - float(src["level"].get("elevation") or 0.0)
    name_of, id_of = renamer(base, copy_id)
    dst = bpy.data.collections.new(f"furniture_{copy_id}")
    parent_collection.children.link(dst)
    bpy.context.view_layer.update()
    objs = list(src["collection"].all_objects)
    made: dict = {}
    for ob in objs:
        new = ob.copy()
        new.name = name_of(ob.name)
        dst.objects.link(new)
        made[ob.name] = new
    shift = Matrix.Translation((0.0, 0.0, dz))
    for ob in objs:
        new = made[ob.name]
        if ob.parent is not None and ob.parent.name in made:
            new.parent = made[ob.parent.name]            # the local transform (basis, parent inverse) is kept
        elif ob.parent is None:
            new.matrix_basis = shift @ ob.matrix_basis
        else:
            new.matrix_world = shift @ ob.matrix_world
        for key in list(new.keys()):
            value = new[key]
            if isinstance(value, str):
                new[key] = id_of(value)
        for mod in new.modifiers:
            for attr in MODIFIER_OBJECT_ATTRS:
                target = getattr(mod, attr, None)
                if target is not None and getattr(target, "name", None) in made:
                    try:
                        setattr(mod, attr, made[target.name])
                    except (AttributeError, TypeError):
                        pass
        for con in new.constraints:
            target = getattr(con, "target", None)
            if target is not None and getattr(target, "name", None) in made:
                con.target = made[target.name]
    name_map = {k: v.name for k, v in made.items()}
    manifest_objects.extend(copy_entries(src["entries"], name_map, base, copy_id, dz))
    objects = {id_of(pid): made[ob.name] for pid, ob in (src["summary"].get("objects") or {}).items()
               if getattr(ob, "name", None) in made}
    return {"summary": copy_summary(src["summary"], base, copy_id, objects), "collection": dst, "objects": len(made)}


def copy_scene_report(report: Optional[dict], base: str, copy_id: str) -> dict:
    """The scene-check report of a copy (pure): the typical floor's, its ids moved, ``typical_copy_of`` the typical
    floor (the copy's objects are the same meshes at the same places one storey up)."""
    tag, new_tag = f"_{base}_", f"_{copy_id}_"
    rep = _renamed(_copy.deepcopy(report or {}), {}, tag, new_tag)
    rep["typical_copy_of"] = base
    return rep
