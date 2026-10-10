"""The gap report (docs/milestone12.md §6.4 D24): per room type and style family, the group members a furnished room
needs against the library models that stay (``keep`` and ``fix``), with the sources that could fill each gap.

What: ``gap_table(items, statuses, groups=None, cfg)`` -> rows ``{room, group, role, type, family, count, target,
gap}``; ``gaps_markdown(...)`` -> ``gaps.md``. Targets (``audit.yaml gaps``): >= 5 per anchor type and family, >= 3
per partner type and family. A model counts for a family when its ``styles`` hold the family or ``neutral``.

Group needs: ``wenart/furniture/groups.yaml`` when track G has written it (read leniently: a mapping of group
templates with ``room_types`` / ``rooms``, ``anchor`` (a type, a list or ``{type: ...}``) and ``partners`` /
``members`` (types or ``{type, role}``)), else ``BUILTIN_GROUPS`` below (the anchors of
``wenart/furniture/schemas.py ANCHOR_TYPES`` and the partners each group needs).

Why: growth (Poly Haven, ABO style pass, Infinigen fixtures ...) is approved per list; the gap report says what is
missing where, so the lists ask only for what the runs need.

How: pure; deterministic order (room types as listed, families in ``STYLE_FAMILIES`` order).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from wenart.assets.audit import REPO

GROUPS_YAML = REPO / "wenart" / "furniture" / "groups.yaml"

# room type -> [(group, role, types)]; role anchor or partner (built-in fallback for groups.yaml).
BUILTIN_GROUPS: dict[str, list[tuple[str, str, tuple[str, ...]]]] = {
    "living": [("seating", "anchor", ("sofa", "sofa_corner")), ("seating", "partner", ("armchair",)),
               ("seating", "partner", ("table_coffee",)), ("seating", "partner", ("side_table",)),
               ("seating", "partner", ("floor_lamp",)), ("seating", "partner", ("rug",)),
               ("seating", "partner", ("cushion",)), ("seating", "partner", ("throw",)),
               ("media", "anchor", ("tv_unit",)), ("storage", "partner", ("bookshelf",)),
               ("storage", "partner", ("sideboard",)), ("decor", "partner", ("wall_art",)),
               ("decor", "partner", ("plant_large",)), ("decor", "partner", ("vase",)),
               ("light", "partner", ("pendant_light",))],
    "bedroom": [("sleeping", "anchor", ("bed_double",)), ("sleeping", "anchor", ("bed_single",)),
                ("sleeping", "partner", ("nightstand",)), ("sleeping", "partner", ("table_lamp",)),
                ("sleeping", "partner", ("cushion",)), ("sleeping", "partner", ("rug",)),
                ("storage", "anchor", ("wardrobe",)), ("storage", "partner", ("dresser",)),
                ("decor", "partner", ("wall_art",)), ("decor", "partner", ("mirror",)),
                ("light", "partner", ("ceiling_light",))],
    "child": [("sleeping", "anchor", ("bunk_bed",)), ("sleeping", "anchor", ("crib",)),
              ("sleeping", "partner", ("nightstand",)), ("storage", "partner", ("wardrobe",))],
    "dining": [("dining", "anchor", ("table_dining",)), ("dining", "partner", ("chair",)),
               ("dining", "partner", ("pendant_light",)), ("storage", "partner", ("sideboard",)),
               ("storage", "partner", ("display_cabinet",))],
    "kitchen": [("kitchen run", "anchor", ("fridge",)), ("kitchen run", "anchor", ("stove",)),
                ("kitchen run", "anchor", ("sink_kitchen",)), ("kitchen run", "partner", ("tall_cabinet",)),
                ("counter", "partner", ("bar_stool",)), ("decor", "partner", ("bowl",))],
    "bathroom": [("bathroom set", "anchor", ("toilet",)), ("bathroom set", "anchor", ("washbasin",)),
                 ("bathroom set", "anchor", ("bathtub",)), ("bathroom set", "anchor", ("shower",)),
                 ("bathroom set", "partner", ("washing_machine",)), ("bathroom set", "partner", ("mirror",))],
    "hall": [("entry", "anchor", ("console_table",)), ("entry", "partner", ("shoe_cabinet",)),
             ("entry", "partner", ("bench",)), ("entry", "partner", ("mirror",))],
    "work": [("work", "anchor", ("desk",)), ("work", "partner", ("office_chair",)),
             ("work", "partner", ("bookshelf",)), ("work", "partner", ("table_lamp",))],
}

# type -> the growth sources that have it (docs/milestone12.md §6.4 "Sources checked 10 Oct 2026").
SOURCES_FOR: dict[str, tuple[str, ...]] = {
    "toilet": ("infinigen",), "washbasin": ("infinigen",), "bathtub": ("infinigen",), "sink_kitchen": ("infinigen",),
    "stove": ("infinigen",), "fridge": ("parametric (track S)", "infinigen (beverage fridge)"),
    "shower": ("parametric (track S)",), "washing_machine": ("parametric (track S)",),
    "throw": ("procedural textiles (track S)",), "curtain": ("procedural textiles (track S)",),
    "blind": ("procedural textiles (track S)",),
    "cushion": ("abo (pillows)",), "rug": ("abo (rugs)",), "wall_art": ("abo (wall art)", "polyhaven (frames)"),
    "bowl": ("polyhaven", "gso", "infinigen"), "books": ("polyhaven", "infinigen"), "vase": ("polyhaven",),
    "basket": ("polyhaven",), "clock": ("polyhaven",), "mirror": ("polyhaven", "abo"),
    "pendant_light": ("polyhaven (chandeliers, pendants)", "abo"), "ceiling_light": ("polyhaven", "abo"),
    "plant_small": ("gso (pots)", "polyhaven"), "plant_large": ("polyhaven",), "candle": ("polyhaven",),
    "bed_double": ("abo (style pass, headboards)",), "bed_single": ("abo (style pass)",),
}
DEFAULT_SOURCES = ("abo (style pass)", "polyhaven")


def families() -> list[str]:
    from wenart.style import vocabulary as V
    return [name for name, _ in V.STYLE_FAMILIES]


def _types_of(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        t = value.get("type") or value.get("types")
        return _types_of(t) if t else []
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            out += _types_of(v)
        return out
    return []


def groups_from_yaml(path: Path = GROUPS_YAML) -> Optional[dict]:
    """Room type -> [(group, role, types)] read from track G's ``groups.yaml``, or None (missing or no group read)."""
    if not Path(path).is_file():
        return None
    import yaml
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 - an unreadable file: the built-in table
        return None
    templates = data.get("groups") or data.get("templates") or data
    if not isinstance(templates, dict):
        return None
    out: dict = {}
    for name, g in templates.items():
        if not isinstance(g, dict):
            continue
        rooms = g.get("room_types") or g.get("rooms") or g.get("room_type") or []
        rooms = [rooms] if isinstance(rooms, str) else list(rooms)
        anchor = _types_of(g.get("anchor"))
        partners = g.get("partners") or g.get("members") or []
        rows = [(str(name), "anchor", (t,)) for t in anchor]
        for p in partners if isinstance(partners, list) else [partners]:
            role = p.get("role", "partner") if isinstance(p, dict) else "partner"
            for t in _types_of(p):
                if t not in anchor:
                    rows.append((str(name), "anchor" if role == "anchor" else "partner", (t,)))
        for room in rooms:
            out.setdefault(str(room), []).extend(rows)
    return out or None


def kept_count(items: list[dict], statuses: dict, ftype: str, family: str, keep=("keep", "fix")) -> int:
    n = 0
    for it in items:
        if it["type"] != ftype or statuses.get(it["id"]) not in keep:
            continue
        styles = it.get("styles") or []
        if family in styles or "neutral" in styles:
            n += 1
    return n


def gap_table(items: list[dict], statuses: dict, groups: Optional[dict] = None, cfg: Optional[dict] = None,
              keep=("keep", "fix")) -> list[dict]:
    cfg = (cfg or {}).get("gaps") or {}
    a_min, p_min = int(cfg.get("anchor_min", 5)), int(cfg.get("partner_min", 3))
    groups = groups or BUILTIN_GROUPS
    rows = []
    for room, members in groups.items():
        seen = set()
        for group, role, types in members:
            for t in types:
                if (group, t) in seen:
                    continue
                seen.add((group, t))
                target = a_min if role == "anchor" else p_min
                for fam in families():
                    n = kept_count(items, statuses, t, fam, keep)
                    rows.append({"room": room, "group": group, "role": role, "type": t, "family": fam, "count": n,
                                 "target": target, "gap": max(0, target - n)})
    return rows


def gaps_markdown(rows: list[dict], title: str, note: str = "") -> str:
    fams = families()
    lines = [f"# {title}", ""]
    if note:
        lines += [note, ""]
    lines += ["Counts of the models that stay per type and style family (a model counts for a family when its styles "
              "hold it or `neutral`); **bold** = below the target (anchor >= 5, partner >= 3).", ""]
    by_room: dict = {}
    for r in rows:
        by_room.setdefault(r["room"], []).append(r)
    for room, rs in by_room.items():
        lines += [f"## {room}", "", "| group | role | type | " + " | ".join(fams) + " |",
                  "|---|---|---|" + "---|" * len(fams)]
        order: list = []
        for r in rs:
            if (r["group"], r["role"], r["type"]) not in order:
                order.append((r["group"], r["role"], r["type"]))
        for g, role, t in order:
            cells = []
            for fam in fams:
                r = next(x for x in rs if x["type"] == t and x["group"] == g and x["family"] == fam)
                cells.append(f"**{r['count']}**" if r["gap"] else str(r["count"]))
            lines.append(f"| {g} | {role} | {t} | " + " | ".join(cells) + " |")
        lines.append("")
    gaps: dict = {}
    for r in rows:
        if r["gap"]:
            gaps.setdefault(r["type"], set()).add(r["family"])
    lines += ["## Gaps and the sources that could fill them", "", "| type | families below target | sources |",
              "|---|---|---|"]
    for t in sorted(gaps):
        fs = [f for f in fams if f in gaps[t]]
        lines.append(f"| {t} | {', '.join(fs)} | {', '.join(SOURCES_FOR.get(t, DEFAULT_SOURCES))} |")
    lines.append("")
    return "\n".join(lines)
