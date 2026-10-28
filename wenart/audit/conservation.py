"""Conservation: nothing disappears between stages (26 Oct 2026, user: "there was a veranda in real06, it has been
fully missed ... the issue is not just veranda ... develop a system to understand the problem kinds and prevent it
happening").

What: the building of every stage (the reading's ``building.json``, the fit's, the layout's, the decor's, the agent's,
the final one, the build's ``scene/building_built.json``) and the scene manifest, compared element by element:

- C1 an element of a stage is missing from the next one, and nothing in the next one names it (a merge, a
  replacement, a removal record);
- C2 an element planned to be built becomes ``build: false`` at a stage with no reason;
- C3 an element the final building plans to build (rooms, walls, openings, built pieces, site areas and site
  symbols) has no object in the scene;
- C4 a drawn element (vector or raster evidence) that no rule or model typed (``unknown``, ``other``) and nothing
  built or explained: it is lost while it looks kept (real06: 42 drawn site circles of kind "other");
- C5 a source label the reading kept as a site area without an outline and did not build (real06: "VERANDA 22,80 m²");
- C6 (info) every element the build did not build with the reason it gave (the scene manifest's ``not_built``,
  ``decor_skipped``, the site's ``not_built``): these are explained, not lost, and each reason is listed so the AI
  auditor (``argus_ai``) judges whether it is a good one (real06: 42 site circles "of kind 'other' not built (no
  model)": an explanation that hides a loss).

- C7 a drawn piece left out as not a piece (a rug outline, a detail, a mark) although an AI pass named a furniture
  type that fits its size (``named_left_out``; 27 Oct 2026).

Each finding names the stage boundary where it happened (``owner``), so the kind ``lost`` is caught where it arises,
for every element type, in every project. Pure; no limits: every element is checked.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from wenart.audit import kinds as K

# stage -> its building file under a project's output folder (the results layout is ``from_results``)
STAGE_FILES = (("reading", "building.json"), ("fit", "building_fitted.json"), ("layout", "building_furnished.json"),
               ("decor", "building_decor.json"), ("agent", "building_agent.json"), ("final", "building_final.json"),
               ("build", "scene/building_built.json"))
# the collections compared: (name, path in the building)
COLLECTIONS = (("rooms", ("rooms",)), ("walls", ("walls",)), ("openings", ("openings",)),
               ("furniture", ("furniture",)), ("site_areas", ("site", "areas")), ("site_symbols", ("site", "decor")),
               ("trees", ("site", "trees")), ("pools", ("site", "pools")), ("platforms", ("site", "platforms")),
               ("outdoor_spaces", ("site", "outdoor_spaces")))
CRITICAL_COLLECTIONS = ("rooms", "walls", "openings", "site_areas", "pools", "platforms", "outdoor_spaces")
REASON_KEYS = ("not_built_reason", "inferred_as", "replaced_by", "merged_into", "removed_reason", "reason", "note",
               "not_furniture", "explained")
UNTYPED = ("unknown", "other", "", None)
TYPED_COLLECTIONS = ("furniture", "site_symbols")      # the collections whose elements need a type to be built


def _items(building: dict, path: tuple) -> list[dict]:
    node = building
    for p in path:
        node = (node or {}).get(p) if isinstance(node, dict) else None
    return [x for x in node or [] if isinstance(x, dict) and x.get("id")] if isinstance(node, list) else []


def _reason(el: dict) -> Optional[str]:
    for k in REASON_KEYS:
        v = el.get(k)
        if v:
            return str(v) if not isinstance(v, dict) else str(v.get("reason") or v)
    return None


def _drawn(el: dict) -> bool:
    return any(isinstance(e, dict) and e.get("method") in ("vector", "raster") for e in el.get("evidence") or [])


def _type(el: dict):
    return el.get("type") if "type" in el else el.get("kind")


def named_at(obj, needle: str, path: str = "") -> Optional[tuple[str, str]]:
    """``(path, text)`` of the first place in ``obj`` whose string names ``needle`` (the id itself or a text with it),
    e.g. ``("agent_overrides.removed[3]", "f_L0_044 ...")``; None when nothing names it."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            got = named_at(v, needle, f"{path}.{k}" if path else str(k))
            if got:
                return got
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            got = named_at(v, needle, f"{path}[{i}]")
            if got:
                return got
    elif isinstance(obj, str) and (obj == needle or needle in obj):
        return path, obj
    return None


def between(name_a: str, a: dict, name_b: str, b: dict) -> list[dict]:
    """C1 and C2 between two consecutive stages. An element the next stage only names (a merge, a replacement, a
    removal record) is a C1 note (``info``) with the place and the text that name it: Argus AI judges whether that is
    a reason or a loss."""
    out = []
    text_b = None
    for coll, path in COLLECTIONS:
        later = {x["id"]: x for x in _items(b, path)}
        for el in _items(a, path):
            nxt = later.get(el["id"])
            if nxt is None:
                if text_b is None:
                    text_b = json.dumps(b, ensure_ascii=False)
                if f'{el["id"]}' in text_b:
                    where = named_at(b, el["id"]) or ("?", "")
                    out.append(K.finding("conservation", "C1", "info", el["id"],
                                         f"{el['id']} ({_type(el)}) of the {name_a} stage is gone after the {name_b} "
                                         f"stage, named in {where[0]}: {str(where[1])[:200]}", owner=name_b,
                                         evidence={"collection": coll, "from": name_a, "to": name_b,
                                                   "named_in": where[0]}))
                    continue
                out.append(K.finding("conservation", "C1", "critical" if coll in CRITICAL_COLLECTIONS else "major",
                                     el["id"], f"{coll[:-1] if coll.endswith('s') else coll} {el['id']} "
                                     f"({_type(el)}) of the {name_a} stage is missing after the {name_b} stage and "
                                     f"nothing there names it", owner=name_b,
                                     evidence={"collection": coll, "from": name_a, "to": name_b}))
                continue
            if el.get("build") is not False and nxt.get("build") is False and not _reason(nxt):
                out.append(K.finding("conservation", "C2", "major", el["id"],
                                     f"{el['id']} ({_type(nxt)}) was to be built after the {name_a} stage and is not "
                                     f"built after the {name_b} stage, with no reason", owner=name_b,
                                     evidence={"collection": coll, "from": name_a, "to": name_b}))
    return out


def _scene_ids(manifest: dict) -> set:
    ids = set()
    for o in manifest.get("objects") or []:
        for k in ("element_id", "wenart_id", "name", "parent", "entrance"):
            if o.get(k):
                ids.add(str(o[k]))
    return ids


def explained(manifest: Optional[dict]) -> dict:
    """``{id: reason}`` of the elements the build left out with a reason (module docstring, C6)."""
    out = {}
    m = manifest if isinstance(manifest, dict) else {}
    furn = m.get("furniture") if isinstance(m.get("furniture"), dict) else {}
    site = m.get("site") if isinstance(m.get("site"), dict) else {}
    for src in (furn.get("not_built"), furn.get("decor_skipped"), site.get("not_built")):
        for n in src or []:
            if isinstance(n, dict) and n.get("id"):
                out[str(n["id"])] = str(n.get("reason") or "")
    for a in m.get("assumed") or []:
        if isinstance(a, dict) and a.get("parent") and a.get("kind") in ("stair_arrival",):
            out.setdefault(str(a["parent"]), str(a.get("reason") or ""))
    return out


def in_scene(final: dict, manifest: Optional[dict]) -> list[dict]:
    """C3: the elements the final building plans to build with no object in the scene (by id), unless the build
    left them out with a reason (``explained``: C6)."""
    if not isinstance(manifest, dict) or not manifest.get("objects"):
        return []
    ids = _scene_ids(manifest)
    ids |= set(explained(manifest))
    names = " ".join(sorted(ids))
    out = []
    for coll, path in COLLECTIONS:
        for el in _items(final, path):
            if el.get("build") is False:
                continue
            if coll == "furniture" and ((el.get("asset") or {}).get("method") in (None, "none")):
                continue                          # no model fitted: C2 / the fit's record says why
            if coll == "site_areas" and not el.get("polygon"):
                continue                          # C5 below (or built as an outdoor space: that one is checked)
            if el["id"] in ids or el["id"] in names:
                continue
            host = el.get("built_into") if coll == "furniture" else None
            if host and str(host) in ids:
                continue                          # 28 Oct 2026: a hob or fridge built into its counter run's object
            if _type(el) in UNTYPED and coll in TYPED_COLLECTIONS:
                continue                          # C4 names it (untyped: nothing could build it)
            out.append(K.finding("conservation", "C3", "critical" if coll in CRITICAL_COLLECTIONS else "major",
                                 el["id"], f"{el['id']} ({_type(el)}, {coll}) is planned to be built but the scene has "
                                 f"no object for it", owner="build", evidence={"collection": coll}))
    return out


def outdoor_built(final: dict) -> dict:
    """``{site area id: outdoor space id}`` of the labelled site areas built as an outdoor space
    (``site.outdoor_spaces``: ``wenart.levels.outdoor``, a polygon and not ``build: false``)."""
    return {str(o.get("area_id")): str(o.get("id")) for o in _items(final, ("site", "outdoor_spaces"))
            if o.get("area_id") and o.get("polygon") and o.get("build") is not False}


def untyped(final: dict) -> list[dict]:
    """C4 and C5 on the final building. The untyped elements of one collection are one finding (one missing rule),
    every id in its evidence."""
    out = []
    untyped_: dict = {}
    spaces = outdoor_built(final)
    for coll, path in COLLECTIONS:
        for el in _items(final, path):
            if coll == "site_areas":
                if el["id"] in spaces:
                    continue                      # built as the outdoor space that names it
                if el.get("build") is False or not el.get("polygon"):
                    label = el.get("label") or el.get("label_raw") or el["id"]
                    out.append(K.finding("conservation", "C5", "critical", el["id"],
                                         f"the documents label a site area '{label}' and the model does not build it "
                                         f"({_reason(el) or 'no outline, no reason'})", owner="site",
                                         evidence={"collection": coll, "label": label,
                                                   "source": [e.get("entity") for e in el.get("evidence") or []
                                                              if isinstance(e, dict)][:4]},
                                         fix="build_outdoor_space"))
                continue
            if coll in TYPED_COLLECTIONS and _type(el) in UNTYPED and _drawn(el) and not _reason(el):
                untyped_.setdefault(coll, []).append(el)
    for coll, els in untyped_.items():
        ids = [e["id"] for e in els]
        out.append(K.finding("conservation", "C4", "major", ids[0] if len(ids) == 1 else f"{len(ids)} {coll}",
                             f"{len(ids)} drawn {coll.replace('_', ' ')} ({', '.join(ids[:6])}"
                             f"{' ...' if len(ids) > 6 else ''}) that no rule or model typed ('{_type(els[0])}'): "
                             f"nothing builds them and nothing explains them", owner="reading",
                             evidence={"collection": coll, "ids": ids,
                                       "source": [e.get("entity") for el in els[:4] for e in el.get("evidence") or []
                                                  if isinstance(e, dict)][:8]},
                             fix="type_site_symbols" if coll == "site_symbols" else "retype_piece"))
    return out


LEFT_OUT_AS = ("rug", "detail", "mark", "decor")    # the reading's "not a piece" kinds (``inferred_as``, ``type``)


def named_left_out(final: dict) -> list[dict]:
    """C7 (27 Oct 2026, pod run 224516: real06's two drawn sofas were left out as "rug outlines" while an AI pass named
    each a sofa; the judge saw a salon without a sofa, and no line named the cause): a drawn piece the reading left out
    as not a piece (a rug or zone outline, a detail, a mark) although an AI pass named a furniture type for it whose
    real product range fits its drawn size. Major, kind ``lost``, owner ``reading``; the fix is the typed action
    ``type_piece`` with that type (Argus carries it out through ``retype_piece``, code checks it)."""
    try:
        from wenart.furniture import sizes as SZ
    except Exception:  # noqa: BLE001 - no size table here: no check
        return []
    out = []
    for el in _items(final, ("furniture",)):
        how = str(el.get("inferred_as") or (el.get("type") if el.get("type") in LEFT_OUT_AS else "") or "")
        if el.get("build") is not False or not _drawn(el) or how not in LEFT_OUT_AS or el.get("not_furniture"):
            continue
        if el.get("detail_of") or el.get("replaced_by"):
            continue                    # 27 Oct 2026 (pod run 091638): a cushion drawn on its sofa is no lost plant
        size = ((el.get("footprint") or {}).get("size") or [])[:2]
        named = sorted({str(c.get("type")) for c in el.get("type_candidates") or [] if isinstance(c, dict)
                        and c.get("type") not in UNTYPED and c.get("type") not in LEFT_OUT_AS})
        fit = [t for t in named if len(size) == 2 and SZ.fits(t, size)]
        if not fit:
            continue
        out.append(K.finding("conservation", "C7", "minor" if how == "detail" else "major", el["id"],
                             f"drawn piece {el['id']} ({float(size[0]):.2f} x {float(size[1]):.2f} m) left out as a "
                             f"{how} ({el.get('inferred_reason') or el.get('not_built_reason') or 'no reason'}) although an AI pass named it {' / '.join(fit)}, "
                             f"which fits its size: a reason that hides a lost piece", owner="reading", kind="lost",
                             evidence={"named": fit, "left_out_as": how, "room": el.get("room_id")},
                             fix={"action": "type_piece", "element_id": el["id"], "type": fit[0]}))
    return out


def reasons(manifest: Optional[dict]) -> list[dict]:
    """C6 (info): one finding per reason given for leaving elements out, with the ids it covers."""
    groups: dict = {}
    for eid, reason in explained(manifest).items():
        groups.setdefault(reason, []).append(eid)
    return [K.finding("conservation", "C6", "info", ids[0] if len(ids) == 1 else f"{len(ids)} elements",
                      f"not built: {reason or 'no reason'} ({', '.join(ids[:8])}{' ...' if len(ids) > 8 else ''})",
                      owner="build", evidence={"ids": ids, "reason": reason}, kind="lost")
            for reason, ids in sorted(groups.items(), key=lambda kv: -len(kv[1]))]


def audit(stages: list[tuple[str, dict]], manifest: Optional[dict] = None) -> dict:
    """``{"findings": [...], "checked": {...}}`` over the stages in order (``[(name, building)]``) and the scene."""
    findings = []
    for (na, a), (nb, b) in zip(stages, stages[1:]):
        findings += between(na, a, nb, b)
    if stages:
        findings += in_scene(stages[-1][1], manifest)
        findings += untyped(stages[-1][1])
        findings += named_left_out(stages[-1][1])
    findings += reasons(manifest)
    checked = {name: sum(len(_items(b, p)) for _c, p in COLLECTIONS) for name, b in stages}
    return {"findings": findings, "checked": checked,
            "counts": {c: sum(1 for f in findings if f["check"] == c) for c in ("C1", "C2", "C3", "C4", "C5", "C6",
                                                                                 "C7")}}


def load(project_out, files: tuple = STAGE_FILES) -> list[tuple[str, dict]]:
    """The stages' buildings of a project's output folder that exist, in order."""
    out = []
    for name, rel in files:
        path = Path(project_out) / rel
        try:
            out.append((name, json.loads(path.read_text(encoding="utf-8"))))
        except (OSError, ValueError):
            continue
    return out


def from_results(results: Path, project: str) -> tuple[list[tuple[str, dict]], Optional[dict]]:
    """The stages and the scene manifest of a collected run (``runs/<job>/results``)."""
    results = Path(results)
    files = tuple((name, f"furniture/{project}/{rel}") for name, rel in STAGE_FILES if not rel.startswith("scene/")) \
        + (("build", f"renders/{project}/building_built.json"),)
    stages = load(results, files)
    try:
        manifest = json.loads((results / "renders" / project / "scene_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        manifest = None
    return stages, manifest
