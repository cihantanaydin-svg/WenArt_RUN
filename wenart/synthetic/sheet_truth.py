"""Ground truth of synthetic-07 (docs/milestone10.md §3.4, §5 row 5).

What: four files, all computed from the layout objects of ``wenart.synthetic.sheet`` and the entity record of
``sheet_writer`` (nothing is measured back from the DXF):

- ``building.json``: the usual building truth of the plan levels (schema-valid, ``wenart.building.validate``): levels L-1,
  L-1b (the open-kitchen alternative), L0, L1 with the M10 fields, walls, openings (with ``operation``), rooms, furniture,
  one page record per region that is read, the two variants.
- ``sheets_truth.json``: what the sheets stage must find: the regions (id, box, class, title, level, variant, registration,
  use), the stray, the levels and variants (the field names of ``sheets.json``, docs/milestone10.md §1.2).
- ``heights_truth.json``: slab tops and thicknesses, floor to floor, ceilings, ground, the roof (the field names of
  ``sheets.json`` ``heights``; plain numbers instead of ``{value, method, evidence}``).
- ``exterior_truth.json``: roof type and outline, facade materials, the openings per facade, the site plan, north.

Why: acceptance row 5 compares every class, level, variant, registration shift (+-1 cm) and height (+-1 cm) with this
truth. Conventions (docs/milestone10.md §1.6b row 1): building frame = the ground-floor plan's frame in metres, origin at
the min corner of its outer faces; ``p_ref = R(rotation) * (p_source * metres_per_unit) + shift_m`` registers a plan onto
the ground-floor drawing; ``transform_to_building`` = the registration followed by the reference's origin step, i.e. for
every region here ``x_m = (X - X0) / 100`` with ``(X0, Y0)`` the sheet position of the region's local origin.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import building as B
from wenart.synthetic import sheet as S
from wenart.synthetic.sheet import CM, Drawing, SheetProject, rnd
from wenart.synthetic.sheet_writer import SheetRecord

CLASS_FOR_PAGE = {"alternative_floor_plan": "floor_plan"}
LANGUAGE = "tr"
GLOSS = {"Açık mutfak": "open kitchen"}


def _num(v: float, n: int = 6) -> float:
    return rnd(v, n) + 0.0


def _ev(method="vector", confidence=1.0, **kw) -> dict:
    return B.evidence(S.FILE_DXF, method, confidence, **kw)


def _transform(d: Drawing) -> list[float]:
    """[0.01, 0, -X0/100, 0, 0.01, -Y0/100]: drawing units -> building metres (plans), -> (s, z) of the section,
    -> (metres from the facade's left end, z) of an elevation."""
    return [S.METRES_PER_UNIT, 0.0, _num(-d.origin[0] / CM), 0.0, S.METRES_PER_UNIT, _num(-d.origin[1] / CM)]


def _shift(project: SheetProject, d: Drawing) -> list[float]:
    """Registration shift: p_ref = p * 0.01 + shift puts the drawing of ``d`` on the ground-floor drawing."""
    gx, gy = project.drawing("ground").origin
    return [_num((gx - d.origin[0]) / CM), _num((gy - d.origin[1]) / CM)]


def _sheet_box(d: Drawing, box_m) -> list[float]:
    ox, oy = d.origin
    return [_num(ox + CM * box_m[0], 3), _num(oy + CM * box_m[1], 3), _num(ox + CM * box_m[2], 3), _num(oy + CM * box_m[3], 3)]


def title_info(d: Drawing, record: SheetRecord) -> Optional[dict]:
    if d.title is None:
        return None
    text = d.title.text.replace("\\P", "\n")
    return {"text": text, "entity": record.one(d.key, "title"), "box": _sheet_box(d, S.text_box_m(d.title)),
            "language": LANGUAGE}


def _features(project: SheetProject, d: Drawing) -> dict:
    g = d.geometry
    count = lambda pred: sum(1 for p in g if pred(p))                          # noqa: E731
    if d.level is not None:
        lv = d.level
        out = {"room_labels": len(lv.rooms), "wall_face_lines": count(lambda p: p.role.startswith("face:")),
               "wall_layer": S.L_WALL, "columns": count(lambda p: p.role.startswith("column:")),
               "door_blocks": sum(1 for o in lv.openings if o.kind == "door"),
               "window_blocks": sum(1 for o in lv.openings if o.kind == "window"),
               "furniture_blocks": len(lv.furniture), "stairs": sum(1 for f in lv.furniture if f.block == S.STAIR_BLOCK)}
        if d.key == "ground":
            out["cut_line"] = "A-A"
        if d.key == "attic":
            out.update(roof_outline=True, roof_ridge_line=True)
        return out
    if d.key == "section":
        return {"slab_bands": 3, "level_marks": len(S.MARKS), "roof_lines": 2, "ground_lines": 2}
    if d.cls == "elevation":
        ops = d.extra["openings"]
        return {"windows": sum(o.kind == "window" for o, *_ in ops), "doors": sum(o.kind == "door" for o, *_ in ops),
                "ground_lines": 1, "hatches": count(lambda p: p.kind == "hatch")}
    if d.key == "site":
        return {"north_arrow": True, "plot_boundary": True, "trees": len(S.TREES), "parking": True, "street_words": ["YOL"]}
    if d.key == "legend":
        return {"samples": 5}
    return {"short_texts": len([p for p in d.prims if p.kind == "text"]), "on_frame_edge": True}


# --------------------------------------------------------------------------
# sheets_truth.json
# --------------------------------------------------------------------------

def _rect_distance(a, b) -> float:
    dx = max(a[0] - b[2], b[0] - a[2], 0.0)
    dy = max(a[1] - b[3], b[1] - a[3], 0.0)
    return math.hypot(dx, dy)


def build_sheets_truth(project: SheetProject, record: SheetRecord, created_utc: str) -> dict:
    ids = project.region_ids()
    ground = ids["ground"]
    regions = []
    for d in project.reading_order():
        box = d.box_cm()
        lv = d.level
        title = title_info(d, record)
        region = {
            "id": ids[d.key], "file": S.FILE_DXF, "sheet": "s1", "page": 1, "box": box,
            "box_m": [_num((box[2] - box[0]) / CM, 3), _num((box[3] - box[1]) / CM, 3)],
            "entities": len(d.prims) + (1 if d.title else 0),
            "geometry_entities": len(d.geometry), "text_entities": len(d.texts), "frame": record.frame,
            "class": d.cls, "class_method": "geometry" if d.cls == "title_block" else "title", "class_confidence": 1.0,
            "status": "verified", "title": title, "features": _features(project, d),
            "level": ({"order": lv.order, "label": lv.label, "id": lv.id, "kind": lv.kind, "method": "title"} if lv else None),
            "variant_group": lv.variant_group if lv else None,
            "variant": lv.variant if lv else None,
            "variant_slug": (B.variant_slug(lv.variant) if lv else None),
            "variant_gloss": GLOSS.get(lv.variant) if lv else None,
            "metres_per_unit": S.METRES_PER_UNIT,
            "transform_to_building": _transform(d) if d.key not in ("legend", "titleblock") else None,
            "registration": None, "use": d.use,
            "ignored_reason": ({"legend": "legend", "titleblock": "title block"}.get(d.key)),
            "evidence": ([_ev(layer=S.L_TEXT, entity=title["entity"], text=title["text"], region_id=ids[d.key],
                              rule="title_keyword")] if title else []),
        }
        if lv is not None or d.key == "site":
            region["registration"] = {
                "reference": None if d.key == "ground" else ground,
                "rotation_deg": 0.0, "shift_m": _shift(project, d) if d.key != "ground" else [0.0, 0.0],
                "residual_m": 0.0, "stairs_aligned": True if lv is not None else None,
                "method_note": ("the reference plan" if d.key == "ground" else
                                "site plan: through its building outline" if d.key == "site" else
                                "a pure shift of the same outline (the method, outline_icp or columns, is the reader's)")}
        regions.append(region)
    frame_box = list(S.FRAME)
    (sx0, sy0), (sx1, sy1) = S.STRAY
    stray_box = [min(sx0, sx1), min(sy0, sy1), max(sx0, sx1), max(sy0, sy1)]
    nearest = min(_rect_distance(stray_box, r["box"]) for r in regions)
    diag = math.hypot(frame_box[2] - frame_box[0], frame_box[3] - frame_box[1])
    return {
        "schema_version": "1.0", "kind": "sheets_truth", "project": project.name, "created_utc": created_utc,
        "documents": [{"file": S.FILE_DXF, "format": "dxf", "converter": None,
                       "units": {"insunits": S.INSUNITS, "metres_per_unit": S.METRES_PER_UNIT, "method": "dxf_insunits",
                                 "conflict": None},
                       "sheets": [{"id": "s1", "space": "model", "box": frame_box,
                                   "frames": [{"entity": record.frame, "box": frame_box}],
                                   "gap_units": _num(0.015 * diag, 3)}]}],
        "regions": regions,
        "stray": [{"file": S.FILE_DXF, "sheet": "s1", "entity": record.stray, "type": "LINE", "layer": "0", "box": stray_box,
                   "distance_m": _num(nearest / CM, 1), "reason": "far outside the frame, 1 entity (< 1 % of the sheet)"}],
        "levels": [
            {"id": "L-1", "order": -1, "label": "Bodrum Kat", "kind": "basement", "base_region": ids["basement"],
             "alternatives": [{"region": ids["basement_alt"], "variant": "Açık mutfak", "slug": "acik-mutfak",
                               "level_id": "L-1b", "base_unclear": False}]},
            {"id": "L0", "order": 0, "label": "Zemin Kat", "kind": "floor", "base_region": ground, "alternatives": []},
            {"id": "L1", "order": 1, "label": "Çatı Katı", "kind": "attic", "base_region": ids["attic"], "alternatives": []}],
        "variants": [
            {"id": "base", "label": "Base", "base": True, "levels": ["L-1", "L0", "L1"],
             "regions": [ids["basement"], ground, ids["attic"]]},
            {"id": B.variant_id("L-1b", "acik-mutfak"), "label": "Bodrum Kat: Açık mutfak (open kitchen)", "base": False,
             "levels": ["L-1b", "L0", "L1"], "regions": [ids["basement_alt"], ground, ids["attic"]]}],
        "conflicts": [], "warnings": [], "needs_review": [],
    }


# --------------------------------------------------------------------------
# heights_truth.json
# --------------------------------------------------------------------------

def build_heights_truth(project: SheetProject, record: SheetRecord) -> dict:
    ids = project.region_ids()
    r = project.roof
    sec = lambda role: record.one("section", role)                            # noqa: E731
    slab = [sec(f"slab:{k}") for k in range(3)]
    mark = [sec(f"mark_tri:{k}") for k in range(3)]
    mark_text = [sec(f"mark_text:{k}") for k in range(3)]
    floors = [(-S.FLOOR_TO_FLOOR, "L-1", -3.0), (0.0, "L0", 0.0), (S.FLOOR_TO_FLOOR, "L1", 3.0)]
    levels = []
    for k, (z, lid, mark_z) in enumerate(floors):
        below_slab, above_slab = (slab[k], slab[k + 1] if k + 1 < 3 else None)
        entry = {"level_id": lid, "floor_z": z,
                 "ceiling_height": (_num(r.ridge_under - z) if lid == "L1" else _num(S.CEILING)),
                 "floor_to_floor": (_num(S.FLOOR_TO_FLOOR) if lid != "L1" else None),
                 "level_mark": mark_z, "level_mark_text": S.MARKS[k][1], "level_mark_target_z": z,
                 "entities": {"floor_slab": below_slab, "slab_above": above_slab, "mark": mark[k], "mark_text": mark_text[k],
                              "mark_line": sec(f"mark_line:{k}")}}
        levels.append(entry)
    return {
        "schema_version": "1.0", "kind": "heights_truth", "project": project.name,
        "section_regions": [ids["section"]], "cut_axis": "y", "cut_at": S.CUT_AT, "flipped": False,
        "cut_line_entity": record.one("ground", "cut:line"),
        "datum": {"value": 0.0, "printed": "±0.00", "entity": mark_text[1]},
        "levels": levels,
        "alternative_levels": {"L-1b": "copies L-1 (floor_z -3.0, ceiling 2.8, floor_to_floor 3.0)"},
        "slabs": [{"between": [None, "L-1"], "thickness": S.SLAB, "z_top": -3.0, "entity": slab[0]},
                  {"between": ["L-1", "L0"], "thickness": S.SLAB, "z_top": 0.0, "entity": slab[1]},
                  {"between": ["L0", "L1"], "thickness": S.SLAB, "z_top": 3.0, "entity": slab[2]}],
        "ground": [{"side": "south", "z": S.GROUND_Z, "entities": [sec("ground:S"), record.one("south", "ground")]},
                   {"side": "north", "z": S.GROUND_Z, "entities": [sec("ground:N")]},
                   {"side": "east", "z": S.GROUND_Z, "entities": [record.one("east", "ground")]}],
        "roof": {
            "eaves_z": _num(r.eaves_top), "ridge_z": _num(r.ridge_top), "eaves_underside_z": _num(r.eaves_under),
            "ridge_underside_z": _num(r.ridge_under), "pitches_deg": [r.pitch_deg], "knee_wall": r.knee,
            "overhang": r.overhang, "thickness": r.thickness, "vertical_thickness": _num(r.vertical_thickness),
            "profile": [[_num(-r.overhang), _num(r.eaves_top)], [_num(r.half), _num(r.ridge_top)],
                        [_num(S.DEPTH + r.overhang), _num(r.eaves_top)]],
            "definitions": {"eaves_z / ridge_z": "top surface of the roof at the outline edge / at the ridge (building z)",
                            "knee_wall": "attic floor to the roof UNDERSIDE at the outer wall face (the outer face line)",
                            "thickness": "perpendicular to the slope; the vertical gap of the drawn band is "
                                         "thickness / cos(pitch)",
                            "overhang": "roof outline beyond the outer wall face, measured in the section"},
            "entities": {"roof": sec("roof"), "knee": [sec("knee:S"), sec("knee:N")]}},
        "attic_ceiling_note": "no flat ceiling part is drawn: the attic ceiling_height is the roof underside at the ridge "
                              "above the attic floor",
    }


# --------------------------------------------------------------------------
# exterior_truth.json
# --------------------------------------------------------------------------

def _opening_positions(project: SheetProject, d: Drawing, record: SheetRecord) -> list[dict]:
    """Per opening seen in an elevation: kind, x from the facade's left end seen from outside (centre and left edge), width,
    sill and head (building z), the plan opening id and level."""
    level_of = {op.id: lv.id for lv in project.levels for op in lv.openings}
    return [{"kind": op.kind, "opening_id": op.id, "level_id": level_of[op.id], "x": _num(x_left + op.width / 2),
             "x_left": x_left, "width": op.width, "sill": z0, "head": z1, "entity": record.one(d.key, f"open:{op.id}")}
            for op, x_left, z0, z1 in sorted(d.extra["openings"], key=lambda t: t[1])]


def build_exterior_truth(project: SheetProject, record: SheetRecord) -> dict:
    ids = project.region_ids()
    r = project.roof
    attic = project.drawing("attic").level
    terrace_room = next(room for room in attic.rooms if room.room_type == "balcony")
    south, east = project.drawing("south"), project.drawing("east")
    walls = {i: w for i, w in enumerate(attic.walls)}
    facade_evidence = {"stone": record.all("south", "plinth_hatch") + record.all("south", "note:stone"),
                       "render_s": record.all("south", "note:render"), "render_e": record.all("east", "note:render")}
    return {
        "schema_version": "1.0", "kind": "exterior_truth", "project": project.name,
        "roof": {
            "type": "gable", "type_source": "section", "also_seen_in": ["elevation", "plan_roof_lines"],
            "outline": [[-r.overhang, -r.overhang], [S.WIDTH + r.overhang, -r.overhang], [S.WIDTH + r.overhang, S.DEPTH + r.overhang],
                        [-r.overhang, S.DEPTH + r.overhang]],
            "outline_entity": record.one("attic", "roof:outline"),
            "ridge_lines": [[[-r.overhang, S.DEPTH / 2], [S.WIDTH + r.overhang, S.DEPTH / 2]]],
            "ridge_entity": record.one("attic", "roof:ridge"), "break_line": None,
            "covering": "clay_tiles", "covering_source": "label", "covering_label": "KİREMİT",
            "covering_entity": record.one("south", "note:roof"),
            "openings": [{"kind": "terrace", "room_id": terrace_room.id, "polygon": [list(p) for p in S.TERRACE],
                          "parapet_wall_ids": [walls[S.S].id, walls[S.E].id],
                          "note": "shown on the attic plan; the elevations draw the roof envelope"}],
        },
        "facade": [
            {"region": ids["south"], "side": "south", "z_range": [0.0, S.PLINTH], "material": "stone_cladding",
             "source": "hatch", "label": "TAŞ KAPLAMA", "entities": facade_evidence["stone"]},
            {"region": ids["south"], "side": "south", "z_range": [S.PLINTH, _num(r.eaves_under)], "material": "render",
             "source": "label", "label": "SIVA", "entities": facade_evidence["render_s"]},
            {"region": ids["east"], "side": "east", "z_range": [0.0, _num(r.ridge_under)], "material": "render",
             "source": "label", "label": "SIVA", "entities": facade_evidence["render_e"]}],
        "openings_seen": [
            {"region": ids["south"], "side": "south", "view_bearing_deg": S.view_bearing_deg("south"), "windows": sum(o.kind == "window" for o, *_ in south.extra["openings"]),
             "doors": sum(o.kind == "door" for o, *_ in south.extra["openings"]),
             "positions_m": _opening_positions(project, south, record),
             "not_seen": "basement openings stand below the ground line (z 0.00) and are not drawn"},
            {"region": ids["east"], "side": "east", "view_bearing_deg": S.view_bearing_deg("east"), "windows": sum(o.kind == "window" for o, *_ in east.extra["openings"]),
             "doors": sum(o.kind == "door" for o, *_ in east.extra["openings"]),
             "positions_m": _opening_positions(project, east, record),
             "not_seen": "basement openings stand below the ground line (z 0.00) and are not drawn"}],
        "site": {
            "region": ids["site"],
            "plot": [list(p) for p in S.PLOT],
            "plot_entity": record.one("site", "plot"),
            "plot_walls": [{"start": [_num(a[0]), _num(a[1])], "end": [_num(b[0]), _num(b[1])], "thickness": S.PLOT_WALL_T,
                            "kind": "plot"} for a, b in S.plot_wall_centre()],
            "plot_wall_entities": [record.one("site", "plot_wall_outer"), record.one("site", "plot_wall_inner")],
            "building_outline": [[0.0, 0.0], [S.WIDTH, 0.0], [S.WIDTH, S.DEPTH], [0.0, S.DEPTH]],
            "building_entity": record.one("site", "building"),
            "parking": [{"polygon": [list(p) for p in S.PARKING], "label": "OTOPARK", "entity": record.one("site", "parking")}],
            "trees": [{"center": list(t), "radius": 1.2, "entity": record.one("site", f"tree:{k}")} for k, t in enumerate(S.TREES)],
            "road": {"polygon": [list(p) for p in S.ROAD], "label": "YOL", "entity": record.one("site", "road")},
            "labels": [{"text": name, "at": list(at), "entity": record.one("site", f"label:{name}")} for name, at in S.SITE_LABELS],
            "paving": [], "grass": [],
        },
        "north": {"value": 0.0, "note": "building +Y is north (the arrow points up the sheet, the plans are not rotated)",
                  "entity": record.one("site", "north"), "letter_entity": record.one("site", "north_n")},
        "balconies": [], "chimneys": [],
        "brief_exterior_words": {"facade": "white render", "roof": "clay tiles", "window_frame": "anthracite aluminium"},
    }



# --------------------------------------------------------------------------
# building.json
# --------------------------------------------------------------------------

LEVEL_DRAWING = {"L-1": "basement", "L-1b": "basement_alt", "L0": "ground", "L1": "attic"}
PAGE_CLASS = {"floor_plan": "floor_plan", "alternative_floor_plan": "floor_plan", "section": "section",
              "elevation": "elevation", "site_plan": "site_plan"}


def build_building_truth(project: SheetProject, record: SheetRecord, created_utc: str, pipeline_commit: str) -> dict:
    ids = project.region_ids()
    building = B.empty_building(project.name, f"projects/{project.name}", pipeline_commit, created_utc=created_utc,
                                brief=project.brief)
    section_rid = ids["section"]

    def slab_ev(k: int) -> dict:
        return _ev(entity=record.one("section", f"slab:{k}"), region_id=section_rid, rule="slab_bands")

    def title_ev(d: Drawing) -> dict:
        info = title_info(d, record)
        return _ev(layer=S.L_TEXT, entity=info["entity"], text=info["text"], region_id=ids[d.key], rule="title_keyword")

    # Document: one page record per region that is read (plans), used for the heights (section) or the exterior.
    pages = []
    for d in sorted((x for x in project.drawings if x.use != "ignored"), key=lambda x: int(ids[x.key][1:])):
        lv = d.level
        pages.append({
            "page": 1, "class": PAGE_CLASS[d.cls], "region_id": ids[d.key], "region_box": d.box_cm(), "region_class": d.cls,
            "variant": lv.variant if lv else None, "skip_reason": None, "kind": "vector",
            "level_id": lv.id if lv else None, "level_label_raw": title_info(d, record)["text"], "classifier": "title",
            "scale": {"metres_per_unit": S.METRES_PER_UNIT, "method": "dxf_insunits", "confidence": 1.0,
                      "evidence": _ev(entity=f"$INSUNITS={S.INSUNITS}")},
            "transform_to_building": _transform(d), "confidence": 1.0, "evidence": [title_ev(d)], "debug_image": None})
    building["documents"].append({"id": "doc_" + B.slugify(S.FILE_DXF), "file": S.FILE_DXF, "format": "dxf", "converter": None,
                                  "unit_system": "metric", "source_kind": "dxf", "pages": pages})

    drawn_in_elevation = {op.id for key in ("south", "east") for op, *_ in project.drawing(key).extra["openings"]}
    r = project.roof
    base_rooms = {rm.label: rm.id for rm in project.levels[0].rooms}
    for lv in project.levels:
        d = project.drawing(LEVEL_DRAWING[lv.id])
        rid = ids[d.key]
        k = {"L-1": 0, "L-1b": 0, "L0": 1, "L1": 2}[lv.id]
        ceiling = _num(r.ridge_under - lv.floor_z) if lv.kind == "attic" else _num(S.CEILING)
        floor_to_floor = None if lv.kind == "attic" else {
            "value": _num(S.FLOOR_TO_FLOOR), "method": "vector", "confidence": 1.0, "evidence": [slab_ev(k), slab_ev(k + 1)]}
        building["levels"].append({
            "id": lv.id, "label": lv.label, "order": lv.order, "elevation": lv.floor_z, "ceiling_height": ceiling,
            "ceiling_height_source": "section", "label_source": "title", "kind": lv.kind,
            "variant_group": lv.variant_group, "variant": lv.variant, "variant_slug": B.variant_slug(lv.variant),
            "base_level_id": lv.base_level_id, "region_id": rid, "elevation_source": "section",
            "floor_to_floor": floor_to_floor, "evidence": [title_ev(d)]})
        for index, wall in enumerate(lv.walls):
            faces = [_ev(layer=S.L_WALL, entity=e, region_id=rid) for e in record.all(d.key, f"face:{index}")]
            building["walls"].append({
                "id": wall.id, "level_id": lv.id, "start": list(wall.start), "end": list(wall.end), "thickness": wall.thickness,
                "height": None, "exterior": wall.exterior, "status": "verified", "evidence": faces})
        for op in lv.openings:
            seen = op.id in drawn_in_elevation
            item = {"id": op.id, "type": op.kind, "level_id": lv.id, "wall_id": lv.walls[op.wall_index].id,
                    "center": list(op.center), "width": op.width,
                    "height": op.clear_height if seen else None, "sill_height": op.sill if seen else None,
                    "swing_side": op.swing_side, "status": "verified",
                    "evidence": [_ev(layer=S.L_DOOR if op.kind == "door" else S.L_WINDOW,
                                     entity=record.one(d.key, f"open:{op.id}"), block=op.block, region_id=rid)]}
            if op.kind == "door":
                item.update(operation=op.operation, operation_source="geometry")
            building["openings"].append(item)
        for room in lv.rooms:
            label_raw = lv.labels[room.label_index].label_raw
            evidence = [_ev(layer=S.L_TEXT, entity=record.one(d.key, f"label:{room.id}"), text=label_raw, region_id=rid),
                        _ev("derived", entity="derived-from:" + ",".join(room.wall_ids), region_id=rid)]
            item = {"id": room.id, "level_id": lv.id, "label": room.label, "label_raw": label_raw, "room_type": room.room_type,
                    "polygon": [list(p) for p in room.polygon], "area_computed": room.area_computed,
                    "area_label": B.normalise_room_label(label_raw)[2],
                    "has_documented_furniture": any(f.room_id == room.id for f in lv.furniture), "style_override": None,
                    "status": "verified", "evidence": evidence}
            if lv.id == "L-1b" and room.label == "Hol":
                item["same_as"] = base_rooms["Hol"]
            building["rooms"].append(item)
        for piece in lv.furniture:
            building["furniture"].append({
                "id": piece.id, "level_id": lv.id, "room_id": piece.room_id, "type": piece.type, "type_raw": piece.block,
                "source": "from_documents",
                "footprint": {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg},
                "front_deg": piece.front_deg(), "height": None, "asset": None, "status": piece.status,
                "evidence": [_ev(layer=S.L_FURN, entity=record.one(d.key, f"furn:{piece.id}"), block=piece.block,
                                 region_id=rid)]})

    alt = project.levels[1]
    open_room = next(rm for rm in alt.rooms if rm.label != "Hol")
    building["variants"] = [
        {"id": "base", "label": "Base", "levels": ["L-1", "L0", "L1"], "base": True, "changes": [], "rooms_changed": [],
         "exterior_changed": False},
        {"id": B.variant_id(alt.id, B.variant_slug(alt.variant)), "label": "Bodrum Kat: Açık mutfak (open kitchen)",
         "levels": ["L-1b", "L0", "L1"], "base": False,
         "changes": [{"variant_group": "vg_L-1", "level_id": "L-1b", "replaces": "L-1"}],
         "rooms_changed": [open_room.id], "exterior_changed": False, "evidence": [title_ev(project.drawing("basement_alt"))]}]
    B.validate(building)
    return building
