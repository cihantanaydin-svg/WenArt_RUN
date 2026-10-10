"""Milestone 10 parts of the final report (docs/milestone10.md §3.1, §3.3 item 6, §2.8).

What: pure functions that turn the Milestone 10 data of a project output into report blocks and Markdown lines.
Each ``*_block`` reads plain dicts (``sheets.json``, the building JSON, ``completion.json``, the scene manifest,
the check manifest, the final manifests of the variants) and returns a small summary dict; each ``*_lines``
turns such a block into Markdown. ``wenart/report/final.py`` calls them and stores the blocks in
``final_manifest.json``.

- ``sheets_block`` / ``sheets_lines``: the "Sheets" section: the regions table (class, level, variant, how it was
  decided, confidence, use), the level and variant groups, strays, the unit check per document, conflicts and the
  debug images.
- ``building_block`` / ``building_lines``: the "Building" section: levels, variants, every height with its
  state (drawn or assumed), slabs, roof, facade, site and the levels left out.
- ``completion_block`` / ``completion_lines``: Feature 1 per room: drawn type and size -> new type and size, the
  pieces the AI added, the proposals that were refused or reverted and why.
- ``exterior_block`` / ``exterior_lines``: the exterior views: the outside looks (documents, brief, style or
  assumed), the views per variant, the elevation check, the roof check, the advisory facade counts and the gate
  decision that holds the exterior polish back.
- ``variants_block`` / ``variants_lines``: one row per variant from its own ``final_manifest.json``.
- ``assumed_lines``: every assumed value of the whole building (heights, slabs, roof, site, outside looks).

Why: the report shows what was read from the documents and what was assumed, per room what the AI changed or
added, and the outside views per variant. Nothing is invented here: a missing block is "not recorded".

How: no file access, no image work and no import of ``final.py`` (it imports this module). Lengths go through
a ``fmt`` function the caller gives (metric or imperial text), so the unit system of the project is kept.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

from wenart.report import common as C

Fmt = Callable[[Any], str]
ASSUMED_SOURCES = ("assumed", "assumed_default")
MAX_STRAYS = 8


def scrub(text: Any, names: Optional[dict]) -> Any:
    """``text`` with every document file name of ``names`` (``{file: shown name}``) replaced by its shown name: a
    private project's free text (conflicts, warnings, stop reasons) names its documents by number only. A name
    that is shown as itself changes nothing."""
    if not isinstance(text, str) or not names:
        return text
    for file in sorted((f for f, shown in names.items() if isinstance(f, str) and f and shown != f),
                       key=len, reverse=True):
        text = text.replace(file, str(names[file]))
    return text


def metres(v: Any) -> str:
    """Default length text: ``3.65 m`` (None -> ``-``)."""
    return "-" if not isinstance(v, (int, float)) or isinstance(v, bool) else f"{float(v):.2f} m"


def _num(v: Any) -> Optional[float]:
    """The number of a plain number or of a ``{value, ...}`` record, else None."""
    if isinstance(v, dict):
        v = v.get("value")
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def state_of(source: Any) -> str:
    """``assumed`` / ``drawn`` / ``unknown`` from a source or method word (``assumed``, ``assumed_default`` and a
    note of ``assumed`` are assumed; a source that is missing is unknown, never drawn)."""
    if source in ASSUMED_SOURCES:
        return "assumed"
    return "drawn" if source else "unknown"


def _rec_state(rec: Any) -> tuple[Optional[float], str, Optional[str]]:
    """``(value, state, source)`` of a ``{value, method}`` record."""
    if not isinstance(rec, dict):
        return _num(rec), "unknown", None
    return _num(rec), state_of(rec.get("method")), rec.get("method")


# --------------------------------------------------------------------------
# Sheets
# --------------------------------------------------------------------------

def sheets_block(sheets: Optional[dict], private: bool, names: Optional[dict] = None,
                 previews: Optional[dict] = None) -> Optional[dict]:
    """The Sheets block of ``sheets.json``: regions with class, how it was decided, level, variant and use; the
    level and variant groups; strays; the unit check per document; the stop reasons, conflicts and warnings; the
    debug images. ``names``: ``{file: shown name}`` (a private project's files are numbered, never named);
    ``previews``: ``{debug image path: JPEG name in final/}``."""
    if not isinstance(sheets, dict):
        return None
    docs = [d for d in sheets.get("documents") or [] if isinstance(d, dict)]
    names = names or {d.get("file"): d.get("file") for d in docs}

    def clean(text: Any) -> Any:
        return scrub(text, names) if private else text

    regions = []
    for r in sheets.get("regions") or []:
        if not isinstance(r, dict):
            continue
        level = r.get("level") if isinstance(r.get("level"), dict) else {}
        title = r.get("title") if isinstance(r.get("title"), dict) else {}
        reg = r.get("registration") if isinstance(r.get("registration"), dict) else {}
        regions.append({"id": r.get("id"), "file": names.get(r.get("file"), r.get("file")), "class": r.get("class"),
                        "class_method": r.get("class_method"), "class_confidence": r.get("class_confidence"),
                        "status": r.get("status"), "title": None if private else title.get("text"),
                        "level": level.get("id"), "level_method": level.get("method"), "variant": r.get("variant"),
                        "variant_group": r.get("variant_group"), "use": r.get("use"),
                        "ignored_reason": clean(r.get("ignored_reason")),
                        "registration_residual_m": reg.get("residual_m"),
                        "conflicts": len(r.get("conflicts") or [])})
    units = []
    for d in docs:
        u = d.get("units") if isinstance(d.get("units"), dict) else {}
        units.append({"file": names.get(d.get("file"), d.get("file")), "format": d.get("format"),
                      "insunits": u.get("insunits"), "metres_per_unit": u.get("metres_per_unit"),
                      "method": u.get("method"), "conflict": clean(u.get("conflict")),
                      "checks": [{"check": c.get("check"), "unit": c.get("unit"), "score": c.get("score"),
                                  "samples": c.get("samples"), "note": clean(c.get("note"))}
                                 for c in u.get("checks") or [] if isinstance(c, dict)]})
    strays = [s for s in sheets.get("stray") or [] if isinstance(s, dict)]
    levels = []
    for lv in sheets.get("levels") or []:
        if isinstance(lv, dict):
            levels.append({"id": lv.get("id"), "label": lv.get("label"), "kind": lv.get("kind"),
                           "order": lv.get("order"), "base_region": lv.get("base_region"),
                           "alternatives": [{"region": a.get("region"), "variant": a.get("variant"),
                                             "level_id": a.get("level_id"), "base_unclear": a.get("base_unclear")}
                                            for a in lv.get("alternatives") or [] if isinstance(a, dict)]})
    variants = [{"id": v.get("id"), "label": v.get("label"), "base": bool(v.get("base")),
                 "levels": list(v.get("levels") or []), "regions": list(v.get("regions") or [])}
                for v in sheets.get("variants") or [] if isinstance(v, dict)]
    heights = sheets.get("heights") if isinstance(sheets.get("heights"), dict) else {}
    use: dict[str, int] = {}
    for r in regions:
        use[str(r["use"])] = use.get(str(r["use"]), 0) + 1
    previews = previews or {}
    return {"regions": regions, "regions_by_use": dict(sorted(use.items())), "levels": levels, "variants": variants,
            "sections": list(heights.get("section_regions") or []), "strays": len(strays),
            "stray_list": [{"entity": s.get("entity"), "type": s.get("type"), "layer": s.get("layer"),
                            "distance_m": s.get("distance_m"), "reason": clean(s.get("reason"))}
                           for s in strays[:MAX_STRAYS]],
            "units": units,
            "needs_review": [{"region": n.get("region"), "reason": clean(n.get("reason"))}
                             for n in sheets.get("needs_review") or [] if isinstance(n, dict)],
            "conflicts": [{"id": c.get("id"), "kind": c.get("kind"), "description": clean(c.get("description")),
                           "resolution": clean(c.get("resolution"))} for c in sheets.get("conflicts") or []
                          if isinstance(c, dict)],
            "warnings": [clean(str(x)) for x in sheets.get("warnings") or []],
            "debug_images": [{"source": src, "preview": prev} for src, prev in previews.items()],
            "report": None, "report_kept_on_volume": None}


def sheets_lines(sheets: dict, private: bool, stopped: bool = True) -> list[str]:
    """The "Sheets" section. ``stopped``: the sheets stage stopped the project (the needs-review report)."""
    if stopped:
        intro = ("The sheets stage split every sheet into drawing regions and classified them before any wall was "
                 "read; it stopped the project for the reasons above. Nothing was guessed or filled in.")
    else:
        used = ", ".join(f"{k} {n}" for k, n in (sheets.get("regions_by_use") or {}).items()) or "none"
        intro = ("The sheets stage split every sheet into drawing regions and classified them before any wall was "
                 f"read. {len(sheets['regions'])} regions (use: {used}). A region is read only when its class says "
                 "it is a plan; everything else is ignored with its reason, never guessed.")
    lines = ["", "## Sheets", "", intro]
    if sheets.get("report"):
        lines += ["", f"Full analysis: [{sheets['report']}]({sheets['report']})."]
    elif sheets.get("report_kept_on_volume"):
        lines += ["", f"Full analysis: `{sheets['report_kept_on_volume']}` (a private project: it stays on the "
                      f"volume, not copied)."]
    if sheets["regions"]:
        lines += ["", "Regions:", ""]
        lines += C.table(["region", "file", "class", "decided by", "status", "level", "variant", "use"],
                         [[r["id"], r["file"], r["class"], f"{r['class_method']} ({C.cell(r['class_confidence'])})",
                           r["status"], (r["level"] or "-") + (f" ({r['level_method']})" if r.get("level_method")
                                                              and r["level_method"] != "title" else ""),
                           r["variant"], r["use"] + (f" ({r['ignored_reason']})" if r.get("ignored_reason") else "")]
                          for r in sheets["regions"]])
    if sheets.get("levels") and not stopped:
        rows = []
        for lv in sheets["levels"]:
            alts = "; ".join(f"{a['region']} {a['variant']} -> {a['level_id']}"
                             + (" (base unclear)" if a.get("base_unclear") else "") for a in lv["alternatives"])
            rows.append([lv["id"], lv["label"], lv["kind"], lv["base_region"], alts or "-"])
        lines += ["", "Levels and their alternative plans (a variant group):", ""]
        lines += C.table(["level", "label", "kind", "base region", "alternatives"], rows)
    if sheets.get("variants") and not stopped:
        lines += ["", "Variants (the base building and one per alternative plan):", ""]
        lines += C.table(["variant", "label", "levels", "regions"],
                         [[v["id"], v["label"], ", ".join(v["levels"]), ", ".join(v["regions"])]
                          for v in sheets["variants"]])
    if sheets.get("sections") and not stopped:
        lines += ["", f"Section regions (heights): {', '.join(str(x) for x in sheets['sections'])}."]
    lines += ["", f"Strays (entities far from every drawing, ignored): {sheets['strays']}."]
    if sheets.get("stray_list"):
        lines += [""] + C.table(["entity", "type", "layer", "distance (m)", "reason"],
                                [[s["entity"], s["type"], s["layer"], C.cell(s["distance_m"], 1), s["reason"]]
                                 for s in sheets["stray_list"]])
        if sheets["strays"] > len(sheets["stray_list"]):
            lines.append(f"... and {sheets['strays'] - len(sheets['stray_list'])} more (sheets.json).")
    if sheets["units"]:
        lines += ["", "Unit check (the drawing unit against the room-area labels, the level marks and the door "
                      "widths):", ""]
        lines += C.table(["file", "format", "metres per unit", "method", "checks", "conflict"],
                         [[u["file"], u["format"], u["metres_per_unit"], u["method"],
                           "; ".join(f"{c['check']} {c['unit']} {C.cell(c['score'])} ({c['samples']})"
                                     for c in u["checks"]) or "-", u["conflict"] or "-"] for u in sheets["units"]])
    if sheets["conflicts"]:
        lines += ["", "Conflicts:", ""]
        lines += C.table(["id", "kind", "description", "resolution"],
                         [[c["id"], c["kind"], c["description"], c["resolution"]] for c in sheets["conflicts"]])
    if sheets["debug_images"]:
        lines += ["", "Debug images (every region boxed and labelled with class, level and variant):", ""]
        for i in sheets["debug_images"]:
            if i["preview"]:
                lines.append(f"- [{i['preview']}]({i['preview']})")
            elif private:
                lines.append(f"- {i['source']} (on the volume, not copied)")
            else:
                lines.append(f"- {i['source']}")
    if sheets["warnings"]:
        lines += ["", "Sheet warnings:", ""] + C.bullets(sheets["warnings"])
    return lines


# --------------------------------------------------------------------------
# Building
# --------------------------------------------------------------------------

def _height_row(item: str, rec: Any, source: Any = None, note: Any = None) -> Optional[dict]:
    """One row of the heights table from a ``{value, method}`` record (or a number and a ``source``)."""
    if isinstance(rec, dict):
        value, st, src = _rec_state(rec)
        note = note or rec.get("note")
    else:
        value, src = _num(rec), source
        st = state_of(source)
    if value is None:
        return None
    return {"item": item, "value": value, "state": st, "from": src, "note": note}


def building_block(b: Optional[dict], private: bool = False) -> Optional[dict]:
    """The Building block: levels, variants, heights (each drawn or assumed), slabs, roof, facade, site and the
    levels left out. None for a building without levels. A private project's elevation titles (text from its
    drawings) are left out, as the region titles of the Sheets block are."""
    if not isinstance(b, dict) or not b.get("levels"):
        return None
    if not (any(b.get(k) for k in ("slabs", "roof", "facade", "variants", "levels_left_out"))
            or any(isinstance(lv, dict) and (lv.get("kind") or lv.get("elevation_source")) for lv in b["levels"])):
        return None                       # a building of Milestone 3-9: no stacked levels, slabs or roof to report
    levels, heights = [], []
    for lv in b["levels"]:
        if not isinstance(lv, dict):
            continue
        levels.append({"id": lv.get("id"), "label": lv.get("label"), "kind": lv.get("kind"), "order": lv.get("order"),
                       "elevation": lv.get("elevation"), "ceiling_height": lv.get("ceiling_height"),
                       "ceiling_height_source": lv.get("ceiling_height_source"),
                       "elevation_source": lv.get("elevation_source"), "variant": lv.get("variant"),
                       "variant_group": lv.get("variant_group"), "region_id": lv.get("region_id"),
                       "label_source": lv.get("label_source")})
        for item, rec, src in ((f"{lv.get('id')} ceiling height", lv.get("ceiling_height"),
                                lv.get("ceiling_height_source")),
                               (f"{lv.get('id')} floor level", lv.get("elevation"), lv.get("elevation_source")),
                               (f"{lv.get('id')} floor to floor", lv.get("floor_to_floor"), None)):
            row = _height_row(item, rec, src)
            if row:
                heights.append(row)
    slabs = []
    for s in b.get("slabs") or []:
        if not isinstance(s, dict):
            continue
        slabs.append({"id": s.get("id"), "above": s.get("above_level_id"), "below": s.get("below_level_id"),
                      "z_top": s.get("z_top"), "thickness": s.get("thickness"),
                      "thickness_source": s.get("thickness_source"), "status": s.get("status"),
                      "voids": len(s.get("openings") or []), "variants": list(s.get("variants") or [])})
        row = _height_row(f"{s.get('id')} thickness", s.get("thickness"), s.get("thickness_source"))
        if row:
            heights.append(row)
    roof = b.get("roof") if isinstance(b.get("roof"), dict) else None
    roof_out = None
    if roof:
        recs = {}
        for key in ("eaves_height", "ridge_height", "overhang", "thickness", "knee_wall"):
            row = _height_row(f"roof {key.replace('_', ' ')}", roof.get(key))
            if row:
                heights.append(row)
                recs[key] = row
        pitches = [_rec_state(p) for p in roof.get("pitches_deg") or []]
        roof_out = {"type": roof.get("type"), "type_source": roof.get("type_source"),
                    "over_level_id": roof.get("over_level_id"), "values": recs,
                    "pitches_deg": [{"value": v, "state": st} for v, st, _ in pitches],
                    "planes": len(roof.get("planes") or []), "openings": len(roof.get("openings") or []),
                    "covering": roof.get("covering"), "covering_colour": roof.get("covering_colour"),
                    "covering_source": roof.get("covering_source"), "assumed": [str(x) for x in roof.get("assumed") or []],
                    "status": roof.get("status")}
    facade = b.get("facade") if isinstance(b.get("facade"), dict) else None
    facade_out = None
    if facade:
        facade_out = {"faces": [{"side": f.get("side"), "wall_id": f.get("wall_id"), "level_id": f.get("level_id"),
                                 "material": f.get("material"), "colour": f.get("colour"), "source": f.get("source")}
                                for f in facade.get("faces") or [] if isinstance(f, dict)],
                      "elevations": [{"region_id": e.get("region_id"), "title": None if private else e.get("title"),
                                      "side": e.get("side"),
                                      "windows": e.get("windows"), "doors": e.get("doors"),
                                      "plan_check": e.get("plan_check")}
                                     for e in facade.get("elevations") or [] if isinstance(e, dict)]}
    site = b.get("site") if isinstance(b.get("site"), dict) else None
    site_out = None
    if site:
        ground = site.get("ground") if isinstance(site.get("ground"), dict) else {}
        north = site.get("north_deg")
        n_val, n_state, n_src = _rec_state(north) if north is not None else (None, "unknown", None)
        for w in site.get("boundary_walls") or []:
            row = _height_row(f"{w.get('id')} height", w.get("height")) if isinstance(w, dict) else None
            if row:
                heights.append(row)
        if n_val is not None:
            heights.append({"item": "north direction (deg)", "value": n_val, "state": n_state, "from": n_src,
                            "note": None, "unit": "deg"})

        def built(key: str) -> int:
            return sum(1 for x in site.get(key) or [] if isinstance(x, dict) and x.get("build", True))

        site_out = {"plot": isinstance(site.get("plot"), dict), "paving": built("paving"), "grass": built("grass"),
                    "parking": built("parking"), "boundary_walls": built("boundary_walls"),
                    "areas": len(site.get("areas") or []), "areas_not_built": sum(
                        1 for a in site.get("areas") or [] if isinstance(a, dict) and a.get("build") is False),
                    # B9 (Milestone 12): the ground level is a {value, method} record; the number is printed
                    "decor": built("decor"), "ground": [{"side": g.get("side"), "z": _num(g.get("z")),
                                                         "state": _rec_state(g.get("z"))[1]}
                                                        for g in ground.get("levels") or [] if isinstance(g, dict)],
                    "terrain": ground.get("terrain"), "light_wells": len(ground.get("light_wells") or []),
                    "north_deg": n_val, "north_state": n_state,
                    "levels": level_summary(b)}
    variants = [{"id": v.get("id"), "label": v.get("label"), "base": bool(v.get("base")),
                 "levels": list(v.get("levels") or []), "rooms_changed": len(v.get("rooms_changed") or []),
                 "exterior_changed": bool(v.get("exterior_changed"))}
                for v in b.get("variants") or [] if isinstance(v, dict)]
    left_out = [{"label": x.get("label"), "order": x.get("order"), "variant": x.get("variant"),
                 "reason": x.get("reason")} for x in b.get("levels_left_out") or [] if isinstance(x, dict)]
    return {"levels": levels, "variants": variants, "heights": heights, "slabs": slabs, "roof": roof_out,
            "facade": facade_out, "site": site_out, "levels_left_out": left_out}


def building_lines(block: dict, fmt: Fmt = metres) -> list[str]:
    """The "Building" section."""
    lines = ["", "## Building", "",
             "The whole building as it was read and built: every level stacked on one frame with its slabs, the roof "
             "over the top level, the facade and the site. Each height says whether a document gave it or it was "
             "assumed (never silently)."]
    lines += ["", "Levels:", ""]
    lines += C.table(["level", "label", "kind", "floor level", "ceiling height", "variant", "region"],
                     [[lv["id"], lv["label"], lv["kind"], f"{fmt(lv['elevation'])} ({lv['elevation_source'] or '-'})",
                       f"{fmt(lv['ceiling_height'])} ({lv['ceiling_height_source'] or '-'})",
                       lv["variant"] or "-", lv["region_id"] or "-"] for lv in block["levels"]])
    if block["levels_left_out"]:
        lines += ["", "Levels left out (not built; the building is built from the rest):", ""]
        lines += C.table(["level", "variant", "reason"], [[x["label"], x["variant"] or "-", x["reason"]]
                                                          for x in block["levels_left_out"]])
    if block["variants"]:
        lines += ["", "Variants:", ""]
        lines += C.table(["variant", "label", "levels", "rooms changed", "outside changed"],
                         [[v["id"], v["label"], ", ".join(v["levels"]), v["rooms_changed"],
                           "yes" if v["exterior_changed"] else "no"] for v in block["variants"]])
    heights = block["heights"]
    if heights:
        rows = []
        for h in heights:
            shown = f"{h['value']:g} deg" if h.get("unit") == "deg" else fmt(h["value"])
            rows.append([h["item"], shown, h["state"], h["from"] or "-", h.get("note") or ""])
        lines += ["", "Heights (drawn = read from a document; assumed = a default, listed again under Assumed "
                      "values):", ""]
        lines += C.table(["item", "value", "state", "from", "note"], rows)
    if block["slabs"]:
        lines += ["", "Slabs:", ""]
        lines += C.table(["slab", "carries level", "top", "thickness", "from", "stair voids", "variants", "status"],
                         [[s["id"], s["above"] or "-", fmt(s["z_top"]), fmt(s["thickness"]),
                           s["thickness_source"] or "-", s["voids"], ", ".join(s["variants"]) or "all", s["status"]]
                          for s in block["slabs"]])
    roof = block["roof"]
    lines += ["", "Roof:", ""]
    if roof is None:
        lines.append("None recorded: the build puts a flat roof slab on the top level.")
    else:
        vals = roof["values"]
        parts = [f"type {roof['type']} ({roof['type_source'] or '-'})", f"over level {roof['over_level_id'] or '-'}"]
        for key, name in (("eaves_height", "eaves"), ("ridge_height", "ridge"), ("overhang", "overhang"),
                          ("thickness", "thickness"), ("knee_wall", "knee wall")):
            if key in vals:
                parts.append(f"{name} {fmt(vals[key]['value'])} ({vals[key]['state']})")
        if roof["pitches_deg"]:
            parts.append("pitch " + ", ".join(f"{p['value']:g} deg ({p['state']})" for p in roof["pitches_deg"]
                                              if p["value"] is not None))
        parts.append(f"{roof['planes']} planes, {roof['openings']} opening(s)")
        parts.append("covering " + (f"{roof['covering']} ({roof['covering_source'] or 'drawn'})"
                                    if roof.get("covering") else "not drawn (outside look: see Exterior views)"))
        lines += C.bullets(parts)
        if roof["assumed"]:
            lines += ["", "Assumed for the roof: " + "; ".join(roof["assumed"]) + "."]
    facade = block["facade"]
    lines += ["", "Facade:", ""]
    if facade is None or not (facade["faces"] or facade["elevations"]):
        lines.append("No facade face or elevation drawn: the outside look is resolved from the brief, the style or "
                     "the defaults (see Exterior views).")
    else:
        if facade["faces"]:
            lines += C.table(["side", "wall", "level", "material", "colour", "source"],
                             [[f["side"], f["wall_id"] or "-", f["level_id"] or "-", f["material"],
                               f["colour"] or "-", f["source"]] for f in facade["faces"]])
        if facade["elevations"]:
            lines += ([""] if facade["faces"] else []) + C.table(["elevation", "title", "side", "windows", "doors", "plan check"],
                                    [[e["region_id"], e["title"] or "-", e["side"], e["windows"], e["doors"],
                                      (e["plan_check"] or "-") if not isinstance(e["plan_check"], dict)
                                      else ", ".join(f"{k} {v}" for k, v in e["plan_check"].items())]
                                     for e in facade["elevations"]])
    site = block["site"]
    lines += ["", "Site:", ""]
    if site is None:
        lines.append("None recorded.")
    else:
        parts = [f"plot {'drawn' if site['plot'] else 'not drawn'}", f"{site['paving']} paving area(s), "
                 f"{site['grass']} grass, {site['parking']} parking built",
                 f"{site['boundary_walls']} boundary wall(s), {site['decor']} decor item(s) built",
                 f"{site['areas']} labelled area(s), {site['areas_not_built']} recorded only (label, not built)"]
        if site["ground"]:
            parts.append("ground levels: " + ", ".join(f"{g['side']} {fmt(g['z'])} ({g.get('state') or 'unknown'})"
                                                       for g in site["ground"]))
        parts.append(f"terrain {site['terrain'] or '-'}, {site['light_wells']} light well(s)")
        if site["north_deg"] is not None:
            parts.append(f"north {site['north_deg']:g} deg ({site['north_state']})")
        lines += C.bullets(parts)
        lines += level_lines(site.get("levels"), fmt)
    return lines


def level_summary(b: dict) -> Optional[dict]:
    """Milestone 12 (docs/milestone12.md §3, track L): the level marks, datum, ground, entrances, plinth, room floors
    and what was inferred (``level_inference``), for the report; None for a building without them."""
    marks = [m for m in b.get("level_marks") or [] if isinstance(m, dict)]
    rec = b.get("level_inference") if isinstance(b.get("level_inference"), dict) else None
    if not marks and rec is None:
        return None
    site = b.get("site") if isinstance(b.get("site"), dict) else {}
    kinds: dict[str, int] = {}
    for m in marks:
        kinds[m.get("kind") or "unknown"] = kinds.get(m.get("kind") or "unknown", 0) + 1
    datum = (b.get("project") or {}).get("datum")
    rooms = [{"room_id": r["id"], "offset": r.get("floor_offset_m"), "source": r.get("floor_source")}
             for r in b.get("rooms") or [] if isinstance(r, dict) and r.get("floor_offset_m")]
    ents = [{"door_id": e.get("door_id"), "threshold_z": e.get("threshold_z"), "ground_z": e.get("ground_z"),
             "rise": e.get("rise"), "solution": e.get("solution"), "main": bool(e.get("main")),
             "risers": (e.get("steps") or {}).get("count"), "riser": (e.get("steps") or {}).get("riser"),
             "ramp": (e.get("ramp") or {}).get("ratio"), "into_air": bool(e.get("into_air")),
             "below_ground": bool(e.get("below_ground"))}
            for e in site.get("entrances") or [] if isinstance(e, dict)]
    plinth = site.get("plinth") if isinstance(site.get("plinth"), dict) else None
    return {"marks": len(marks), "kinds": kinds, "datum": _num(datum), "datum_state": _rec_state(datum)[1]
            if datum is not None else None,
            "symbols": sum(1 for s in b.get("symbols") or [] if isinstance(s, dict) and s.get("kind") == "level_mark"),
            "ground_source": (rec or {}).get("ground_source"), "terrain": ((site.get("ground") or {}).get("terrain")),
            "entrances": ents, "plinth": None if plinth is None else {"top_z": plinth.get("top_z"),
                                                                      "source": plinth.get("source")},
            "rooms": rooms, "inferred": [dict(i) for i in (rec or {}).get("inferred") or []],
            "warnings": list((rec or {}).get("warnings") or []), "flagged": (rec or {}).get("flagged")}


def level_lines(block: Optional[dict], fmt: Fmt = metres) -> list[str]:
    """The report lines of ``level_summary`` (Milestone 12)."""
    if not block:
        return []
    lines = ["", "Levels and ground (Milestone 12):", ""]
    kinds = ", ".join(f"{k} {v}" for k, v in sorted(block["kinds"].items())) or "none"
    parts = [f"{block['marks']} level mark(s) read ({kinds}); {block['symbols']} mark symbol(s) taken out of the "
             f"furniture"]
    if block["datum"] is not None:
        parts.append(f"datum ±0.00 = {block['datum']:.2f} m ({block['datum_state']})")
    parts.append(f"ground from: {block['ground_source'] or '-'}; terrain {block['terrain'] or '-'}")
    if block["plinth"]:
        parts.append(f"plinth top {fmt(block['plinth']['top_z'])} ({block['plinth']['source']})")
    if block["rooms"]:
        parts.append("room floors off their level: " + ", ".join(f"{r['room_id']} {r['offset']:+.2f} m ({r['source']})"
                                                                for r in block["rooms"]))
    lines += C.bullets(parts)
    if block["entrances"]:
        lines += ["", "| Door | Threshold | Ground | Rise | Solution | Main |", "|---|---|---|---|---|---|"]
        for e in block["entrances"]:
            sol = e["solution"]
            if e["risers"]:
                sol += f" ({e['risers']} x {e['riser']:.3f} m)"
            if e["ramp"]:
                sol += f", ramp {e['ramp']}"
            if e["into_air"]:
                sol += " - door into the air (L2)"
            if e["below_ground"]:
                sol += " - below the ground (L3)"
            lines.append(f"| {e['door_id']} | {fmt(e['threshold_z'])} | {fmt(e['ground_z'])} | {fmt(e['rise'])} | "
                         f"{sol} | {'yes' if e['main'] else ''} |")
    if block["inferred"]:
        lines += ["", "Inferred (listed, CLAUDE.md evidence rules):", ""]
        lines += C.bullets([f"{i.get('item')}: {i.get('reason')}" for i in block["inferred"]])
    if block.get("flagged"):
        lines += ["", f"Flagged: {block['flagged']}."]
    return lines


# --------------------------------------------------------------------------
# Feature 1: the AI completion of furnished rooms
# --------------------------------------------------------------------------

def _size_text(size: Any) -> str:
    if isinstance(size, (list, tuple)) and size and all(isinstance(x, (int, float)) for x in size):
        return " x ".join(f"{float(x):.2f}" for x in size)
    return "-"


def completion_block(completion: Optional[dict]) -> Optional[dict]:
    """Per room: drawn type and size -> new type and size, the pieces the AI added, the proposals refused or
    reverted with the reason. None without ``completion.json``."""
    if not isinstance(completion, dict) or not isinstance(completion.get("rooms"), list):
        return None
    settings = completion.get("settings") if isinstance(completion.get("settings"), dict) else {}
    rooms = []
    for r in completion["rooms"]:
        if not isinstance(r, dict):
            continue
        changes, refused = [], []
        drawn_types = {d.get("id"): d.get("type") for d in r.get("drawn") or [] if isinstance(d, dict)}
        for c in r.get("changes") or []:
            if not isinstance(c, dict):
                continue
            applied = c.get("status") == "applied"
            # A reverted change records the drawn piece as ``type`` / ``size`` (what stands in the building) and
            # the AI's proposal as ``agreed_type`` / ``agreed_size``: a refused proposal shows the proposal.
            row = {"id": c.get("id"), "drawn_type": c.get("drawn_type"), "drawn_size": c.get("drawn_size"),
                   "type": c.get("type") if applied else c.get("agreed_type") or c.get("type"),
                   "size": c.get("size") if applied else c.get("agreed_size") or c.get("size"),
                   "status": c.get("status"),
                   "look_only": bool(c.get("look_only")), "shrunk": bool(c.get("shrunk")),
                   "type_proposal": bool(c.get("type_proposal")), "style": c.get("style"),
                   "colour": c.get("colour"), "reason": c.get("reason") or None}
            if applied:
                changes.append(row)
            else:
                refused.append(dict(row, why=c.get("reason") or "reverted by the placer"))
        for c in r.get("refused") or []:
            if isinstance(c, dict):
                refused.append({"id": c.get("id"), "drawn_type": c.get("drawn_type") or drawn_types.get(c.get("id")),
                                "type": c.get("type"),
                                "size": c.get("size"), "status": c.get("status") or "refused",
                                "why": c.get("reason") or "refused"})
        dropped = [{"type": d.get("type"), "why": "no free place passed the placer checks"
                    + (f" ({d['reason']})" if d.get("reason") else "")}
                   for d in r.get("dropped") or [] if isinstance(d, dict)]
        rooms.append({"room_id": r.get("room_id"), "label": r.get("label"), "room_type": r.get("room_type"),
                      "state": r.get("state"), "reason": r.get("reason") or None, "changes": changes,
                      "added": [{"id": a.get("id"), "type": a.get("type"), "size": a.get("size"),
                                 "confidence": a.get("confidence"), "method": a.get("method"),
                                 "mirrored_from": a.get("mirrored_from")}
                                for a in r.get("added") or [] if isinstance(a, dict)],
                      "refused": refused, "dropped": dropped,
                      "wall_cabinets": len(r.get("wall_cabinets") or []),
                      "unplaceable_drawn": sorted((r.get("drawn_layout") or {}).get("pieces") or {})})
    # ``Settings.to_dict`` writes the brief keys; the short names are read for a completion made by hand.
    return {"mode": settings.get("furnished_rooms", settings.get("mode")),
            "keep_size": settings.get("furnished_rooms_keep_size", settings.get("keep_size")),
            "keep_rooms": [str(x) for x in settings.get("furnished_rooms_keep") or []],
            "assumed": list(settings.get("assumed") or []),
            "model": completion.get("model"), "rooms": rooms,
            "changes_applied": completion.get("changes_applied"), "pieces_added": completion.get("pieces_added"),
            "wall_cabinets": completion.get("wall_cabinets"),
            "locked_violations": [str(v) for v in completion.get("locked_violations") or []]}


def completion_lines(block: dict, fmt: Fmt = metres) -> list[str]:
    """The Feature 1 section: what the AI changed, added and was refused, per room."""
    keep = block.get("mode") == "keep"
    lines = ["", "## AI completion of furnished rooms (Feature 1)", "",
             f"Mode `furnished_rooms: {block.get('mode') or '-'}`"
             + (", sizes kept" if block.get("keep_size") else "")
             + (f" (assumed: {', '.join(block['assumed'])})" if block.get("assumed") else "") + ". "
             + (f"Rooms kept as drawn in complete mode: {', '.join(block['keep_rooms'])}. "
                if block.get("keep_rooms") and not keep else "")
             + ("Drawn pieces are only restyled; nothing is added." if keep else
                "Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type "
                "(within the room type's types), size, height and look (it stays `from_documents`, "
                "`modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type "
                "misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change "
                "needs both AI passes."),
             "", f"{block.get('changes_applied') or 0} change(s) applied, {block.get('pieces_added') or 0} piece(s) "
                 f"added, {block.get('wall_cabinets') or 0} wall cabinet run(s)."]
    if block["locked_violations"]:
        lines += ["", "Locked-rule violations (the furnished building was not written):", ""]
        lines += C.bullets(block["locked_violations"])
    for r in block["rooms"]:
        body = []
        for c in r["changes"]:
            kind = ("look only" if c["look_only"] else "type proposal (the drawn type was unclear)"
                    if c["type_proposal"] else "changed") + (", shrunk to fit" if c["shrunk"] else "")
            body.append(f"changed {c['id']}: {c['drawn_type']} {_size_text(c['drawn_size'])} -> {c['type']} "
                        f"{_size_text(c['size'])} ({kind})")
        for a in r["added"]:
            body.append(f"added {a['id']}: {a['type']} {_size_text(a['size'])} (confidence "
                        f"{C.cell(a['confidence'])}, {a['method'] or '-'}"
                        + (f", mirrored from {a['mirrored_from']}" if a.get("mirrored_from") else "") + ")")
        if r["wall_cabinets"]:
            body.append(f"{r['wall_cabinets']} wall cabinet run(s) over the drawn counter")
        for x in r["refused"]:
            size = f" (proposed size {_size_text(x['size'])})" if _size_text(x.get("size")) != "-" else ""
            if x.get("id"):
                drawn = f" {x['drawn_type']}" if x.get("drawn_type") else ""
                body.append(f"refused {x['id']}{drawn} -> {x.get('type')}: {x['why']}{size}")
            else:
                body.append(f"refused to add {x.get('type')}: {x['why']}")
        for d in r["dropped"]:
            body.append(f"not placed {d['type']}: {d['why']}")
        if r["unplaceable_drawn"]:
            body.append("drawn pieces that already fail a placer check as drawn (kept, never moved): "
                        + ", ".join(r["unplaceable_drawn"]))
        lines += ["", f"### {r['label'] or r['room_id']} ({r['room_id']}, {r['room_type']}): {r['state']}"
                  + (f" ({r['reason']})" if r.get("reason") else ""), ""]
        lines += C.bullets(body, empty="No change, no addition.")
    return lines


def drawn_block(check: Optional[dict]) -> Optional[dict]:
    """The drawn-piece check of the check manifest (every drawn piece against the source plan: anchor +-5 cm,
    front +-1 deg, same wall, the locked rules): counts, the failed pieces, the locked violations and the notes.
    None when the check manifest has none."""
    d = (check or {}).get("drawn_check") if isinstance(check, dict) else None
    if not isinstance(d, dict):
        return None
    failed = set(d.get("failed") or [])
    return {"reference": d.get("reference"), "mode": d.get("mode"), "tolerance_m": d.get("tolerance_m"),
            "tolerance_deg": d.get("tolerance_deg"), "pieces": len(d.get("pieces") or []),
            "checked": d.get("checked"), "ok": d.get("ok"), "failed": sorted(failed),
            "modified": len(d.get("modified") or []), "proposals": list(d.get("proposals") or []),
            "violations": [str(v) for v in d.get("violations") or []], "notes": [str(n) for n in d.get("notes") or []],
            "failed_rows": [{"id": r.get("id"), "type": r.get("type"), "drawn_type": r.get("drawn_type"),
                             "anchor_distance_m": r.get("anchor_distance_m"), "front_turn_deg": r.get("front_turn_deg"),
                             "same_wall": r.get("same_wall"), "notes": list(r.get("notes") or [])}
                            for r in d.get("pieces") or [] if isinstance(r, dict) and r.get("id") in failed]}


def drawn_lines(block: dict) -> list[str]:
    """The drawn-piece check as report lines (part of the Feature 1 section)."""
    lines = ["", "### Drawn pieces against the source plan", "",
             f"Reference: {block.get('reference')}; mode `{block.get('mode')}`. {block['checked']} of "
             f"{block['pieces']} drawn piece(s) checked: anchor within {block.get('tolerance_m')} m, front within "
             f"{block.get('tolerance_deg')} deg, the same wall; {block['ok']} ok, {len(block['failed'])} failed; "
             f"{block['modified']} changed by the AI."]
    if block["failed_rows"]:
        lines += [""] + C.table(["piece", "type (drawn)", "anchor moved (m)", "front turned (deg)", "same wall", "notes"],
                                [[r["id"], f"{r['type']} ({r['drawn_type']})", r["anchor_distance_m"],
                                  r["front_turn_deg"], r["same_wall"], "; ".join(r["notes"]) or "-"]
                                 for r in block["failed_rows"]])
    if block["violations"]:
        lines += ["", "Locked-rule violations:", ""] + C.bullets(block["violations"])
    if block["notes"]:
        lines += [""] + C.bullets(block["notes"])
    return lines


# --------------------------------------------------------------------------
# Exterior views
# --------------------------------------------------------------------------

def exterior_block(scene: Optional[dict], check: Optional[dict], views: list[dict], gate: Optional[dict],
                   variant: str = "base") -> Optional[dict]:
    """The exterior views of one project output: the outside looks (with their source and whether they are
    assumed), the views and the cameras that were dropped, the roof and facade checks of each view, the elevation
    check and the gate decision for the exterior polish. None when the scene has no exterior camera and no
    exterior look."""
    scene = scene if isinstance(scene, dict) else {}
    cams = [c for c in scene.get("cameras") or [] if isinstance(c, dict) and c.get("kind") == "exterior"]
    dropped = [{"name": c.get("name"), "view": c.get("view"), "sides": list(c.get("sides") or []),
                "reason": c.get("dropped_reason")} for c in scene.get("cameras_dropped") or [] if isinstance(c, dict)]
    looks_in = scene.get("exterior_looks") if isinstance(scene.get("exterior_looks"), dict) else {}
    if not cams and not dropped and not looks_in:
        return None
    looks = [{"slot": slot, "material": v.get("material"), "colour": v.get("colour"), "source": v.get("source"),
              "assumed": bool(v.get("assumed")), "reason": v.get("reason"), "warnings": list(v.get("warnings") or [])}
             for slot, v in looks_in.items() if isinstance(v, dict)]
    by_cam = {v["camera"]: v for v in views if v.get("view_kind") == "exterior"}
    rows = []
    for c in cams:
        v = by_cam.get(c.get("name")) or {}
        vc = v.get("vision_check") or {}
        ex = (vc.get("exterior") or {})
        roof = ex.get("roof") or {}
        facades = vc.get("facades") or {}
        rows.append({"camera": c.get("name"), "view": c.get("view"), "sides": list(c.get("sides") or []),
                     "variant": c.get("variant") or variant, "region_id": c.get("region_id"),
                     "rendered": bool(v), "final": v.get("final"), "reason": v.get("reason"),
                     "roof": roof.get("result"), "roof_note": roof.get("note"),
                     "facades": {side: {"result": f.get("result"), "windows": f.get("windows"),
                                        "doors": f.get("doors")} for side, f in facades.items()
                                 if isinstance(f, dict)},
                     "seen_not_planned": list(ex.get("seen_not_planned") or []),
                     "planned_not_seen": list(ex.get("planned_not_seen") or []),
                     "needs_review": bool(v.get("needs_review"))})
    elev = (check or {}).get("elevation_check") if isinstance(check, dict) else None
    return {"variant": variant, "looks": looks, "views": rows, "dropped": dropped,
            "elevation": None if not isinstance(elev, dict) else {
                "source": elev.get("source"), "summary": elev.get("summary") or {},
                "facades": [{"side": f.get("side"), "region_id": f.get("region_id"), "result": f.get("result"),
                             "drawn": f.get("drawn"), "building": {k: (f.get("building") or {}).get(k)
                                                                   for k in ("windows", "doors")}
                             if f.get("building") else None, "counts": f.get("counts"),
                             "notes": list(f.get("notes") or [])} for f in elev.get("facades") or []],
                "roof": elev.get("roof"), "north": elev.get("north"), "north_source": elev.get("north_source"),
                "warnings": list(elev.get("warnings") or [])},
            "gate": gate}


def exterior_lines(block: dict, sheets: Optional[dict] = None, fmt: Fmt = metres) -> list[str]:
    """The "Exterior views" section. ``sheets``: ``{variant: contact sheet name}`` of ``write_images``."""
    lines = ["", "## Exterior views", ""]
    n_rendered = sum(1 for v in block["views"] if v["rendered"])
    lines.append(f"{n_rendered} of {len(block['views'])} exterior view(s) of variant `{block['variant']}` rendered"
                 + (f"; {len(block['dropped'])} dropped (no camera place worked)" if block["dropped"] else "") + ".")
    if sheets:
        lines.append("")
    for name, sheet in (sheets or {}).items():
        lines.append(f"- contact sheet of `{name}`: [{sheet}]({sheet})")
    g = block.get("gate")
    if g is not None:
        lines += ["", f"Gate for the exterior polish: **{g.get('decision')}** "
                      + ("(polish allowed)" if g.get("polish_allowed") else
                         "(exterior views stay the Cycles render)")
                  + (": " + "; ".join(str(r) for r in g.get("reasons")[:3]) if g.get("reasons") else "") + "."]
    if block["views"]:
        lines += ["", "Views:", ""]
        lines += C.table(["view", "kind", "sides", "region", "final", "roof", "facade counts (advisory)",
                          "review"],
                         [[v["camera"], v["view"], ", ".join(v["sides"]) or "-", v["region_id"] or "-",
                           (v["final"] or "not rendered") + (f" ({v['reason']})" if v.get("reason") else ""),
                           v["roof"] or "-",
                           "; ".join(f"{s}: {f['result']}" for s, f in v["facades"].items()) or "-",
                           "yes" if v["needs_review"] else "no"] for v in block["views"]])
    if block["dropped"]:
        lines += ["", "Dropped views:", ""]
        lines += C.table(["view", "kind", "sides", "reason"],
                         [[d["name"], d["view"], ", ".join(d["sides"]) or "-", d["reason"]] for d in block["dropped"]])
    if block["looks"]:
        lines += ["", "Outside looks (documents > brief > style > fallback; assumed ones are also listed under "
                      "Assumed values):", ""]
        lines += C.table(["slot", "material", "colour", "source", "assumed", "reason"],
                         [[x["slot"], x["material"], x["colour"] or "-", x["source"],
                           "yes" if x["assumed"] else "no", x["reason"]] for x in block["looks"]])
        warn = [w for x in block["looks"] for w in x["warnings"]]
        if warn:
            lines += [""] + C.bullets(warn)
    elev = block.get("elevation")
    lines += ["", "Elevation check (window and door counts and positions per facade, building JSON against the "
                  "drawn elevation; built eaves and ridge against the section; deterministic):", ""]
    if elev is None:
        lines.append("Not run (no check manifest of this run).")
    else:
        s = elev["summary"]
        lines.append(f"Source: {elev.get('source') or '-'}. {s.get('facades', 0)} facade(s): {s.get('ok', 0)} ok, "
                     f"{s.get('mismatch', 0)} mismatch, {s.get('not_checked', 0)} not checked; roof "
                     f"{s.get('roof') or '-'}.")
        if elev["facades"]:
            lines += [""] + C.table(["elevation", "side", "drawn win/door", "built win/door", "result", "notes"],
                                    [[f["region_id"], f["side"],
                                      "{windows}/{doors}".format(**(f["drawn"] or {"windows": "-", "doors": "-"})),
                                      "{windows}/{doors}".format(**f["building"]) if f["building"] else "-",
                                      f["result"], "; ".join(f["notes"]) or "-"] for f in elev["facades"]])
        roof = elev.get("roof") or {}
        built, drawn = roof.get("built") or {}, roof.get("drawn") or {}
        lines += ["", "Roof heights: built " + (", ".join(f"{k} {fmt(v)}" for k, v in built.items() if k in
                                                       ("eaves", "ridge") and v is not None) or "-")
                  + "; drawn " + (", ".join(f"{k} {fmt(v['value'])} ({v.get('method')})" for k, v in drawn.items())
                                  or "-") + f"; result {roof.get('result') or '-'}."]
        if roof.get("notes"):
            lines += C.bullets(roof["notes"])
        if elev["warnings"]:
            lines += [""] + C.bullets(elev["warnings"])
    return lines


# --------------------------------------------------------------------------
# Variants
# --------------------------------------------------------------------------

def variants_block(building: Optional[dict], manifests: dict, base_exterior: list[str],
                   current: str = "base") -> Optional[dict]:
    """One row per variant of the building JSON with what its own ``final/final_manifest.json`` says
    (``manifests``: ``{variant id: manifest | None}``). An alternative whose outside is unchanged lists the base
    exterior views (``base_exterior``: their cameras) instead of rendering its own."""
    variants = [v for v in (building or {}).get("variants") or [] if isinstance(v, dict) and v.get("id")]
    if len(variants) <= 1:
        return None
    rows = []
    for v in variants:
        vid = v["id"]
        m = manifests.get(vid)
        views = [x for x in (m or {}).get("views") or [] if isinstance(x, dict)]
        own_ext = [x["camera"] for x in views if x.get("view_kind") == "exterior"]
        own_int = [x for x in views if x.get("view_kind") != "exterior"]
        if vid == current:
            exterior = "its own views (this report)"
        elif v.get("exterior_changed"):
            exterior = f"its own {len(own_ext)} view(s)" if m else "changed: its views are not reported yet"
        else:
            exterior = "unchanged: the base views (" + (", ".join(base_exterior) or "none rendered") + ")"
        rows.append({"id": vid, "label": v.get("label"), "base": bool(v.get("base")), "levels": list(v.get("levels") or []),
                     "rooms_changed": list(v.get("rooms_changed") or []),
                     "exterior_changed": bool(v.get("exterior_changed")), "exterior": exterior,
                     "reported": m is not None, "status": (m or {}).get("status"),
                     "interior_views": [x["camera"] for x in own_int], "exterior_views": own_ext,
                     "polished": sum(x.get("final") == "polished" for x in views),
                     "cycles": sum(x.get("final") == "cycles" for x in views),
                     "final_mismatches": sum(int(x.get("final_mismatches") or 0) for x in views),
                     "needs_review": sum(bool(x.get("needs_review")) for x in views),
                     "report": f"variants/{vid}/final/final_report.md" if vid != "base" and m is not None else None})
    return {"variants": rows, "current": current}


def variants_lines(block: dict, sheets: Optional[dict] = None) -> list[str]:
    """The "Variants" section. ``sheets``: ``{name: contact sheet file}`` of the per-variant sheets."""
    lines = ["", "## Variants", "",
             "One building per drawn alternative plan: the base and, for each alternative, the same building with "
             "that level replaced. An alternative renders only the rooms it changes, and its exterior views only "
             "when its outside differs (otherwise the base views stand for it). Each alternative has its own "
             "report in its sub-output (paths below, relative to the project output)."]
    lines += [""] + C.table(["variant", "label", "rooms changed", "outside", "interior views", "polished / Cycles",
                             "mismatches", "report"],
                            [[v["id"], v["label"], ", ".join(v["rooms_changed"]) or "-", v["exterior"],
                              ", ".join(v["interior_views"]) or ("not reported" if not v["reported"] else "-"),
                              f"{v['polished']} / {v['cycles']}" if v["reported"] else "-",
                              v["final_mismatches"] if v["reported"] else "-", v["report"] or "-"]
                             for v in block["variants"]])
    if sheets:
        lines.append("")
    for name, sheet in (sheets or {}).items():
        lines.append(f"- {name}: [{sheet}]({sheet})")
    missing = [v["id"] for v in block["variants"] if not v["reported"] and v["id"] != block["current"]]
    if missing:
        lines += ["", "No `variants/<id>/final/final_manifest.json` yet for: " + ", ".join(missing)
                  + " (the variant was not rendered or its report did not run)."]
    return lines


# --------------------------------------------------------------------------
# Assumed values
# --------------------------------------------------------------------------

def assumed_lines(building: Optional[dict], scene: Optional[dict], fmt: Fmt = metres) -> list[str]:
    """Every assumed value of the Milestone 10 data, one line each: heights and thicknesses that no document gave,
    the assumed parts of the roof, the site's ground and north, and each outside look that is a fallback."""
    out: list[str] = []
    block = building_block(building)
    for h in (block or {}).get("heights") or []:
        # The ceiling heights are listed by ``final.assumed_summary`` already (with the level title).
        if h["state"] == "assumed" and not h["item"].endswith(" ceiling height"):
            shown = f"{h['value']:g} deg" if h.get("unit") == "deg" else fmt(h["value"])
            out.append(f"{h['item']}: {shown} ({h['from']}{'; ' + h['note'] if h.get('note') else ''})")
    roof = (block or {}).get("roof") or {}
    for a in roof.get("assumed") or []:
        out.append(f"roof: {a} assumed")
    if (block or {}).get("roof") and roof.get("covering") is None:
        out.append("roof covering: not drawn (the outside look decides, see below)")
    site = (block or {}).get("site") or {}
    if site and not site.get("ground"):
        out.append("site ground: flat at 0.00 m (no ground level drawn)")
    looks = (scene or {}).get("exterior_looks")
    for slot, v in (looks.items() if isinstance(looks, dict) else []):
        if isinstance(v, dict) and v.get("assumed"):
            out.append(f"outside look {slot}: {v.get('material')}" + (f" in {v['colour']}" if v.get("colour") else "")
                       + f" ({v.get('source')}: {v.get('reason')})")
    return out
