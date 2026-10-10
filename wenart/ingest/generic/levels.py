"""The pipeline's level step (docs/milestone12.md §3.1–§3.3, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026): ``apply_levels(build, works) -> None`` is called by ``pipeline.run_project`` once every
level is assembled, before ``reading.read_furniture`` and the type inference. It reads every level mark of the
project's drawings (texts, block attributes, mark symbols; ``wenart.levels.marks``) into ``building["level_marks"]``,
moves furniture pieces that are level-mark symbols to ``building["symbols"]`` (kind ``level_mark``) and fills the
level fields of §3.2 (``wenart.levels.model.infer_levels``). ``works``: ``{page key: PageWork}`` of the pipeline.

How (thin; the rules are pure functions in ``wenart.levels.read`` and ``wenart.levels.model``):

1. every text of every page (``LevelExtraction.texts``: DXF TEXT / MTEXT / ATTRIB with its ``attrib_tag``, PDF and
   OCR words) goes to building metres with the page's ``transform_to_building`` (its box centre), with its level and
   evidence; the section's level marks come from ``sheets.json`` (``build.sheets["heights"]``);
2. ``read.read_marks`` (marks, datum, conflicts), ``read.classify`` (kind by position), ``read.mark_symbols`` (pieces
   that are mark symbols move to ``symbols``), ``read.drawn_ramps``;
3. ``project.datum`` is set from the marks when the sections gave none; the conflicts go to the building's conflicts,
   the warnings to its warnings (``levels: ...``);
4. ``model.infer_levels`` with the project's brief; the result replaces the building in place (``build.building`` is
   the dict the pipeline keeps writing to).
"""
from __future__ import annotations

from wenart import geometry as G


def _texts(works: dict) -> list[dict]:
    out = []
    for key in sorted(works, key=lambda k: str(k)):
        work = works[key]
        ex = work.extraction
        if ex is None or ex.transform_to_building is None:
            continue
        level_id = work.record.level_id
        for t in ex.texts or []:
            if not t.text or not str(t.text).strip():
                continue
            box = t.box or [t.start[0], t.start[1], t.start[0], t.start[1]]
            centre = ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)
            point = G.apply_affine(ex.transform_to_building, centre)
            ev = dict(t.evidence or {"file": ex.file, "method": "vector", "confidence": 1.0, "entity": t.entity})
            if ex.file and not ev.get("file"):
                ev["file"] = ex.file
            if work.record.format == "pdf":
                ev.setdefault("page", work.record.page)
            out.append({"text": str(t.text), "point": (round(point[0], 4), round(point[1], 4)), "level_id": level_id,
                        "entity": t.entity, "evidence": ev, "attrib_tag": ev.get("attrib_tag")})
    return out


def apply_levels(build, works: dict) -> None:
    from wenart.levels import model as LMOD
    from wenart.levels import read as RD

    b = build.building
    params = LMOD.level_params(LMOD._brief_of(b, None))
    texts = _texts(works)
    section = (getattr(build, "sheets", None) or {}).get("heights")
    res = RD.read_marks(texts, b, params, section)
    marks = res["marks"]
    warnings = list(res["warnings"]) + RD.classify(marks, b, params)
    for c in res["conflicts"]:
        build.conflict(c["kind"], c["element_ids"], c["description"], c["resolution"])
    datum = res["datum"]
    if datum is not None and (b["project"].get("datum") or {}).get("value") is None:
        b["project"]["datum"] = {"value": round(float(datum["value"]), 3) + 0.0, "method": "vector", "confidence": 1.0,
                                 "evidence": [dict(e) for e in datum["evidence"]][:2] or
                                 [{"file": "", "method": "vector", "confidence": 1.0}],
                                 "note": f"±0.00 = {datum['value']:.2f} from the level mark(s) "
                                         f"{', '.join(datum['sources'])}"}
    # Level-mark symbols are never furniture (bug B11).
    moved = RD.mark_symbols(b, marks)
    if moved:
        gone = {m["piece_id"] for m in moved}
        b["furniture"] = [f for f in b.get("furniture") or [] if f["id"] not in gone]
        symbols = b.setdefault("symbols", [])
        for m in moved:
            symbols.append(m["symbol"])
            for mk in marks:
                if mk["id"] in m["mark_ids"] and "symbol" not in mk["used_for"]:
                    mk["used_for"].append("symbol")
            warnings.append(f"{m['piece_id']} moved to symbols ({m['symbol']['id']}): {m['symbol']['reason']}")
    ramps = RD.drawn_ramps(texts, b, params)
    if ramps:
        site = b.get("site") if isinstance(b.get("site"), dict) else None
        if site is None:
            site = b["site"] = {"boundary_walls": [], "areas": [], "decor": [], "openings": []}
        site["drawn_ramps"] = ramps
    b["level_marks"] = [{k: v for k, v in m.items() if k not in ("kind_hint", "bare", "group")} for m in marks]
    for m, rec in zip(marks, b["level_marks"]):
        if m.get("group"):
            rec["block_ref"] = m["group"]
    new = LMOD.infer_levels(b)
    rec = new.get("level_inference") or {}
    for c in rec.get("conflicts") or []:
        build.conflict(c["kind"], c["element_ids"], c["description"], c["resolution"])
    rec["conflicts_copied"] = True
    kinds: dict[str, int] = {}
    for m in new.get("level_marks") or []:
        kinds[m.get("kind") or "unknown"] = kinds.get(m.get("kind") or "unknown", 0) + 1
    summary = (f"levels: {len(marks)} level mark(s) read ({', '.join(f'{k} {v}' for k, v in sorted(kinds.items()))})"
               if marks else "levels: no level mark read")
    if datum is not None:
        summary += f"; datum ±0.00 = {datum['value']:.2f}"
    summary += f"; ground: {rec.get('ground_source') or '-'}"
    ents = ((new.get("site") or {}).get("entrances") or []) if isinstance(new.get("site"), dict) else []
    if ents:
        summary += f"; {len(ents)} entrance(s): " + ", ".join(f"{e['door_id']} {e['solution']}" for e in ents)
    build.warn(summary)
    for w in warnings + list(rec.get("warnings") or []):
        build.warn(f"levels: {w}")
    build.building.clear()
    build.building.update(new)
