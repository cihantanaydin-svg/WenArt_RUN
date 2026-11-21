"""A drafting style drawn from the Turkish profile (21 Nov 2026): one per converted project, varied within the profile.

What: ``sample_style(profile, rng)`` picks the layer name of every role, the text heights, the size-tag, area-text,
level-mark, title and scale forms, the label spelling and case, the hatch pattern, the window symbol, the dimension
form, the axis grid, the units and ``$INSUNITS``, each with the profile's frequencies (``turkish_style.json``; a layer
name is weighted by the number of projects that use it, a text form by its share). ``label_for(type, rng, style)``
writes a Turkish room label of a room type, ``area_text``, ``level_text``, ``tag_texts``, ``title_text`` the texts.

Why: the user asked that the dataset projects look like Turkish plans; a reader tested on one look overfits it, so
every project draws with another mix of the conventions the user's offices use.

How: pure functions of the profile and a seeded ``random.Random``; the shapes of the profile (digits folded to 9) are
turned into templates (``{w}/{h}``, ``A:{a}m2``, ``+{z}``).
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Optional

from wenart import building as B
from wenart.ingest.generic import layer_names as LN
from wenart.textfold import fold_ascii

# the Turkish spelling of the folded words of the label vocabulary (the profile stores labels folded)
TR_WORDS = {"COCUK": "ÇOCUK", "ODASI": "ODASI", "ASANSOR": "ASANSÖR", "MERDIVEN": "MERDİVEN", "DUS": "DUŞ",
            "KORIDOR": "KORİDOR", "GIRIS": "GİRİŞ", "GIRISI": "GİRİŞİ", "KILER": "KİLER", "SAFT": "ŞAFT",
            "TESISAT": "TESİSAT", "BOSLUK": "BOŞLUK", "GALERI": "GALERİ", "HOLU": "HOLÜ", "KIS": "KIŞ",
            "BAHCESI": "BAHÇESİ", "YASAMA": "YAŞAMA", "CAMASIR": "ÇAMAŞIR", "ZEMIN": "ZEMİN", "OLCEK": "ÖLÇEK",
            "EBEVEYN": "EBEVEYN", "BANYOSU": "BANYOSU", "ALANI": "ALANI", "ODASI.": "ODASI."}
# room type -> label candidates (folded) used when the profile has none of that type
DEFAULT_LABELS = {"living": ["SALON", "OTURMA ODASI"], "bedroom": ["YATAK ODASI", "ODA", "COCUK ODASI"],
                  "kitchen": ["MUTFAK"], "bathroom": ["BANYO"], "wc": ["WC"], "hall": ["ANTRE", "HOL", "KORIDOR"],
                  "balcony": ["BALKON"], "storage": ["KILER", "DEPO"], "shaft": ["SAFT", "ASANSOR"],
                  "stair": ["MERDIVEN"], "dining": ["YEMEK ODASI"], "technical": ["TESISAT ODASI"],
                  "other": ["ODA"]}
LABEL_WORDS_OK = re.compile(r"^[A-Z .+\-/]{2,20}$")
FALLBACK_LAYERS = {"wall": "DUVAR", "plaster": "SIVA", "structure": "KOLON", "door": "KAPI", "window": "PENCERE",
                   "stair": "MERDIVEN", "furniture": "TEFRIS", "dimension": "OLCU", "text": "YAZI", "hatch": "TARAMA",
                   "axis": "AKS", "sanitary": "VITRIFIYE"}


def _weighted(rng: random.Random, table: dict, by: str = "projects", keep=None) -> Optional[str]:
    items = [(k, float(v.get(by) or 0) + 0.01 * float(v.get("share") or 0)) for k, v in (table or {}).items()
             if keep is None or keep(k)]
    items = [(k, w) for k, w in items if w > 0]
    if not items:
        return None
    total = sum(w for _, w in items)
    x = rng.random() * total
    for k, w in items:
        x -= w
        if x <= 0:
            return k
    return items[-1][0]


def _template(shape: str, names: tuple) -> str:
    """A shape (digits folded to 9) -> a format template: the digit groups in order become ``names``."""
    out, i = [], 0
    for part in re.split(r"(9+(?:[.,]9+)?)", shape):
        if re.fullmatch(r"9+(?:[.,]9+)?", part or "") and i < len(names):
            out.append("{" + names[i] + "}")
            i += 1
        else:
            out.append(part.replace("{", "").replace("}", ""))
    return "".join(out)


@dataclass
class Style:
    layers: dict
    heights: dict
    door_tag: str                 # template with {w} {h}
    window_tag: str               # template with {w} {h} [{s}]
    two_text_tags: bool
    area_tpl: str                 # template with {a}
    area_decimals: int
    area_sep: str
    area_lower: bool
    level_tpl: str                # '+{z}' / '+ {z}' / '±{z}'
    level_sep: str
    ground_mark: str              # '±0.00' / '+0.00'
    title_upper: str              # '{n}. KAT PLANI' ...
    title_level: bool             # '(+3.00) ' before the title
    scale_text: str               # 'ÖLÇEK:1/50' ...
    scale_inline: bool
    turkish_letters: bool
    title_case_labels: bool
    hatch_pattern: str
    hatch_on_wall_layer: bool
    window_lines: int
    window_sill: bool
    dims_as_entities: bool
    axes: bool
    unit: str                     # cm | mm | paper50 (1 unit = 50 m: drawn on paper metres at 1/50)
    insunits: int
    storey_m: float
    seed: int = 0
    extra: dict = field(default_factory=dict)

    @property
    def units_per_metre(self) -> float:
        return {"cm": 100.0, "mm": 1000.0, "m": 1.0, "paper50": 0.02}[self.unit]

    def summary(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if k != "extra"}


def _text_layer_ok(name: str) -> bool:
    role = LN.layer_role(name)
    return role in (None, "text") and "$" not in name and len(name) <= 24


def _height(rng, profile, kind, default):
    h = _weighted(rng, (profile.get("text_heights_m") or {}).get(kind) or {}, by="share")
    return float(h) if h else default


def sample_style(profile: dict, rng: random.Random, seed: int = 0) -> Style:
    lay = profile.get("layers") or {}
    layers = {}
    for role, fb in FALLBACK_LAYERS.items():
        name = _weighted(rng, lay.get(role) or {}, keep=lambda k, role=role: LN.layer_role(k) == role
                         and len(k) <= 24)
        layers[role] = name or fb
    tl = profile.get("text_layers") or {}
    for kind, fb in (("room_label", layers["text"]), ("area", layers["text"]), ("door_tag", layers["text"]),
                     ("window_tag", layers["text"]), ("level", layers["text"]), ("title", layers["text"])):
        layers[kind] = _weighted(rng, tl.get(kind) or {}, keep=_text_layer_ok) or fb
    if rng.random() < 0.3:                         # some offices write the area under the label on the label's layer
        layers["area"] = layers["room_label"]
    heights = {"room_label": _height(rng, profile, "room_label", 0.15), "area": _height(rng, profile, "area", 0.1),
               "door_tag": _height(rng, profile, "door_tag", 0.09),
               "window_tag": _height(rng, profile, "window_tag", 0.09),
               "level": _height(rng, profile, "level", 0.175), "title": max(0.25, _height(rng, profile, "title", 0.4)),
               "dimension": float(_weighted(rng, profile.get("dimension_text_m") or {}, by="share") or 0.15)}
    heights["area"] = min(heights["area"], heights["room_label"])
    sh = profile.get("shapes") or {}
    tag_ok = lambda k: bool(re.fullmatch(r"[A-Z]{0,2}:?\s?9+(\s?[X/]\s?9+){1,2}", k))       # noqa: E731
    door_tag = _template(_weighted(rng, sh.get("door_tag") or {}, keep=tag_ok) or "99/999", ("w", "h"))
    win_tag = _template(_weighted(rng, sh.get("window_tag") or {}, keep=tag_ok) or "999/999",
                        ("w", "h", "s"))
    area_shape = _weighted(rng, sh.get("area") or {},
                           keep=lambda k: "M9" in k or "M²" in k) or "A:99.99M9"
    m = re.search(r"9+([.,])(9+)", area_shape)
    area_sep, area_dec = (m.group(1), len(m.group(2))) if m else (".", 2)
    area_tpl = re.sub(r"9+(?:[.,]9+)?", "{a}", area_shape, count=1).replace("M9", "M2")
    lvl_shape = _weighted(rng, sh.get("level") or {}) or "+9.99"
    level_sep = "," if "," in lvl_shape else "."
    sign = lvl_shape[0] if lvl_shape[0] in "+±-" else "+"
    level_tpl = ("+" if sign == "-" else sign) + (" " if lvl_shape[1:2] == " " else "") + "{z}"
    title_upper = rng.choice(["{n}. KAT PLANI", "{n}.KAT PLANI", "{n}. NORMAL KAT PLANI", "{n}.NORMAL KAT PLANI"])
    scale = rng.choice(["ÖLÇEK:1/50", "ÖLÇEK : 1/50", "Ö:1/50", "1/50", "ÖLÇEK 1/50"])
    sp = profile.get("label_spelling") or {}
    tr_share = (sp.get("turkish_letters") or {}).get("projects", 1) / max(1, sum(
        (v or {}).get("projects", 0) for v in sp.values()))
    hatch_tbl = {k.split("|", 1)[1]: v for k, v in (profile.get("hatch") or {}).items()
                 if k.split("|")[0] in ("other", "wall", "structure", "plaster", "hatch")}
    pattern = _weighted(rng, hatch_tbl, keep=lambda k: k.split(",")[0] in ("SOLID", "ANSI31", "ANSI32", "ANSI33",
                                                                           "ANSI35", "ANSI37", "AR-CONC")) or "SOLID"
    units = profile.get("units") or {"cm": 1}
    unit_tbl = {"cm": units.get("cm", 0), "mm": units.get("mm", 0),
                "paper50": sum(v for k, v in units.items() if "50" in k)}
    unit = _weighted(rng, {k: {"projects": v} for k, v in unit_tbl.items()}) or "cm"
    ins = profile.get("insunits") or {"5": 1}
    insunits = int(_weighted(rng, {k: {"projects": v} for k, v in ins.items()}) or 5)
    if unit == "cm" and insunits not in (0, 4, 5):
        insunits = 5
    storeys = (profile.get("assumed") or {}).get("storey_height_m") or {"3.00": 1.0}
    storey = float(_weighted(rng, {k: {"share": v} for k, v in storeys.items()}, by="share") or 3.0)
    axis_projects = sum((v or {}).get("projects", 0) for v in (lay.get("axis") or {}).values())
    return Style(layers=layers, heights=heights, door_tag=door_tag, window_tag=win_tag,
                 two_text_tags=rng.random() < float((profile.get("assumed") or {}).get("two_text_tag_share", 0.15)),
                 area_tpl=area_tpl, area_decimals=area_dec, area_sep=area_sep, area_lower=rng.random() < 0.5,
                 level_tpl=level_tpl, level_sep=level_sep, ground_mark="±0.00" if rng.random() < 0.6 else "+0.00",
                 title_upper=title_upper, title_level=rng.random() < 0.2, scale_text=scale,
                 scale_inline=rng.random() < 0.3, turkish_letters=rng.random() < max(0.2, tr_share),
                 title_case_labels=rng.random() < 0.05, hatch_pattern=pattern.split(",")[0],
                 hatch_on_wall_layer=rng.random() < 0.5, window_lines=rng.choice([3, 4, 4]),
                 window_sill=rng.random() < 0.4, dims_as_entities=rng.random() < 0.5,
                 axes=rng.random() < min(0.8, axis_projects / max(1, profile.get("projects", 1))),
                 unit=unit, insunits=insunits, storey_m=storey, seed=seed)


# --- texts ----------------------------------------------------------------------------------------------------------

def spell(folded: str, style: Style) -> str:
    """A folded label in the style's spelling (Turkish letters or ASCII) and case."""
    words = folded.split(" ")
    text = " ".join(TR_WORDS.get(w, w) for w in words) if style.turkish_letters else folded
    if style.title_case_labels:
        text = " ".join(w[:1] + w[1:].replace("I", "ı").replace("İ", "i").lower() for w in text.split(" "))
    return text


def label_candidates(profile: dict, room_type: str) -> list[tuple[str, float]]:
    out = []
    for lab, v in (profile.get("room_labels") or {}).items():
        if LABEL_WORDS_OK.match(lab) and B.room_type_for(lab) == room_type:
            out.append((lab, float(v.get("share") or 0)))
    return out or [(lab, 1.0) for lab in DEFAULT_LABELS.get(room_type, ["ODA"])]


def label_for(profile: dict, room_type: str, rng: random.Random, style: Style) -> str:
    cands = label_candidates(profile, room_type)
    total = sum(w for _, w in cands)
    x = rng.random() * total
    for lab, w in cands:
        x -= w
        if x <= 0:
            return spell(lab, style)
    return spell(cands[-1][0], style)


def area_text(area: float, style: Style) -> str:
    a = f"{area:.{style.area_decimals}f}".replace(".", style.area_sep)
    t = style.area_tpl.format(a=a)
    return t.lower() if style.area_lower else t


def level_text(z: float, style: Style) -> str:
    if abs(z) < 1e-9:
        return style.ground_mark.replace(".", style.level_sep)
    return style.level_tpl.format(z=f"{abs(z):.2f}".replace(".", style.level_sep))


def tag_texts(kind: str, w_cm: int, h_cm: int, style: Style, sill_cm: int = 90) -> list[str]:
    """The size tag of a door or window: one text, or two (width over height) in a two-text style."""
    if style.two_text_tags:
        return [str(w_cm), str(h_cm)]
    tpl = style.door_tag if kind == "door" else style.window_tag
    return [tpl.format(w=w_cm, h=h_cm, s=sill_cm)]


def title_text(order: int, z: float, style: Style) -> str:
    base = "ZEMİN KAT PLANI" if order == 0 else style.title_upper.format(n=order)
    if not style.turkish_letters:
        base = fold_ascii(base).upper()
    if style.title_level:
        base = f"({level_text(z, style)}) {base}"
    if style.scale_inline:
        base = f"{base} {style.scale_text if style.turkish_letters else fold_ascii(style.scale_text).upper()}"
    return base
