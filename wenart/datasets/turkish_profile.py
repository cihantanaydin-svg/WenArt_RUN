"""The Turkish drafting profile: how the user's real drawings are drawn, measured as statistics (21 Nov 2026).

What: ``python -m wenart.datasets.turkish_profile measure <dxf> <out.json>`` counts, in one converted DXF, the layer
names per role (``layer_names.layer_role``), the text heights per text kind, the room-label vocabulary and spelling,
the shapes of area texts, door and window size tags, level marks, titles and scale notes (digits folded to ``9``, so a
shape like ``K:99/999`` is kept, never a drawing's text), the door arcs (radius, sweep), the window block line counts,
the hatch patterns per role, the dimension entities and the units. ``build <measure dir> --readings <work>`` adds the
wall thicknesses of the CPU readings (``building.json``) and writes the profile ``wenart/datasets/turkish_style.json``:
per item the frequency over all counted items and the number of projects it occurs in.

Why: the user asked that the dataset test projects look like Turkish plans; the converter
(``wenart.datasets.swiss_dwellings``) draws with these frequencies and varies its style within them, so the reader is
tested on the conventions it meets, not on one look.

How: ezdxf; the model space and every inserted block definition once (an entity on layer ``0`` in a block takes the
INSERT's layer); text heights in metres (``$INSUNITS``, checked against the door arc radii); pure counting, no AI.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path
from typing import Optional

from wenart.ingest.generic import layer_names as LN
from wenart.textfold import fold_ascii

PROFILE_PATH = Path(__file__).with_name("turkish_style.json")
ROOM_WORDS = ("salon", "yasama", "oturma", "gunluk", "yatak", "cocuk", "ebeveyn", "mutfak", "banyo", "dus", "wc",
              "lavabo", "tuvalet", "hol", "antre", "koridor", "giris", "merdiven", "balkon", "teras", "kiler", "depo",
              "oda", "odasi", "yemek", "vestiyer", "giyinme", "camasir", "asansor", "galeri", "sofa", "kat hol",
              "calisma", "misafir", "dolap", "garaj", "otopark", "kazan", "siginak", "saft")
TR_LETTERS = set("İŞÇĞÖÜışçğöü")
RE_AREA = re.compile(r"^(?:[A-Z]{1,4}\s*[:=]\s*)?\d+(?:[.,]\d{1,2})?\s*(?:M2|M²|M\^2|M\s*2)$|"
                     r"^(?:[A-Z]{1,4}\s*[:=]\s*)\d+[.,]\d{1,2}$|^\d+[.,]\d{2}\s*M²?$")
RE_TAG = re.compile(r"^([A-Z]{0,4})\s*([:=.]?)\s*(\d{2,3})\s*([/X])\s*(\d{2,3})(?:\s*/\s*(\d{2,3}))?$")
RE_LEVEL = re.compile(r"^(?:KOT\s*[:=]?\s*)?(±|\+/-|%%P|\+|-)\s*\d{1,2}[.,]\d{2}$")
RE_SCALE = re.compile(r"(?:OLCEK|O\s*[:.]|SCALE|M\s*[:.])?\s*1\s*/\s*(50|100|200|20)\b")
RE_NUM = re.compile(r"^\d+(?:[.,]\d+)?$")
TEXT_KINDS = ("room_label", "area", "door_tag", "window_tag", "level", "title", "scale", "dimension")


def shape(text: str) -> str:
    """A text's shape: upper case, every digit folded to 9, white space collapsed (``a:10.86m2`` -> ``A:99.99M2``)."""
    return re.sub(r"\d", "9", " ".join(str(text).upper().split()))


def _plain(entity) -> str:
    try:
        t = entity.plain_text() if entity.dxftype() == "MTEXT" else entity.dxf.text
    except Exception:                                    # noqa: BLE001 - a broken text is skipped
        return ""
    t = (t or "").replace("%%p", "±").replace("%%P", "±").replace("%%c", "Ø").replace("%%C", "Ø")
    return " ".join(t.split())


def room_words(text: str) -> list[str]:
    words = fold_ascii(text).replace(".", " ").replace("/", " ").replace("-", " ").split()
    return [w for w in words if any(w.startswith(k) for k in ROOM_WORDS)]


def text_kind(text: str, role: Optional[str]) -> Optional[str]:
    """The kind of a text (``TEXT_KINDS``) or None: tags and areas first, then level marks, titles, scale notes,
    room labels; a bare number on a dimension layer is a dimension text."""
    up = " ".join(text.upper().split())
    fa = fold_ascii(text).upper()
    if not up:
        return None
    m = RE_TAG.match(up.replace("İ", "I"))
    if m:
        pre = fold_ascii(m.group(1)).upper()
        if pre.startswith("K") or pre.startswith("D"):
            return "door_tag"
        if pre.startswith("P") or pre.startswith("W"):
            return "window_tag"
        if not pre:
            return "door_tag" if int(m.group(5)) >= 200 else "window_tag"
    if RE_AREA.match(fa.replace(" ", "")) or RE_AREA.match(fa):
        return "area"
    if RE_LEVEL.match(up):
        return "level"
    if "PLAN" in fa and any(w in fa for w in ("KAT", "BODRUM", "ZEMIN", "CATI", "ASMA", "VAZIYET")):
        return "title"
    if RE_SCALE.search(fa) and len(fa) <= 20:
        return "scale"
    if role == "dimension" and RE_NUM.match(up):
        return "dimension"
    if len(up) <= 28 and room_words(text) and sum(c.isdigit() for c in up) <= 2:
        return "room_label"
    return None


class Counter2(collections.Counter):
    def top(self, n: int = 30) -> dict:
        return dict(self.most_common(n))


def _units_guess(insunits: int, radii: list) -> tuple[Optional[float], str]:
    """Metres per drawing unit: the door arcs decide when they are clear (60-130 cm doors), else ``$INSUNITS``."""
    med = sorted(radii)[len(radii) // 2] if radii else None
    for lo, hi, mpu, name in ((0.55, 1.35, 1.0, "m"), (55, 135, 0.01, "cm"), (550, 1350, 0.001, "mm")):
        if med is not None and lo <= med <= hi:
            return mpu, name
    return {4: (0.001, "mm"), 5: (0.01, "cm"), 6: (1.0, "m")}.get(int(insunits or 0), (None, "unknown"))


def measure(path: Path, mpu_known: Optional[float] = None) -> dict:
    """The counts of one DXF (the module docstring); ``mpu_known``: the metres per unit of its CPU reading."""
    import ezdxf

    doc = ezdxf.readfile(str(path))
    styles = {s.dxf.name.upper(): float(s.dxf.get("height", 0) or 0) for s in doc.styles}
    layer_counts: dict = collections.defaultdict(Counter2)       # role -> layer -> entities
    kinds_layers: dict = collections.defaultdict(Counter2)       # text kind -> layer -> texts
    heights: dict = collections.defaultdict(list)                # text kind -> heights (drawing units)
    shapes: dict = collections.defaultdict(Counter2)             # text kind -> shape -> n
    labels, spelling, case = Counter2(), Counter2(), Counter2()
    arcs, door_inserts, hatch = [], Counter2(), Counter2()
    window_block_lines = Counter2()
    dims = Counter2()
    seen_blocks: set = set()
    queue = [(e, None) for e in doc.modelspace()]
    while queue:
        e, ref_layer = queue.pop()
        t = e.dxftype()
        layer = e.dxf.get("layer") or "0"
        if ref_layer and layer == "0":
            layer = ref_layer
        role = LN.layer_role(layer)
        layer_counts[role or "other"][layer] += 1
        if t == "INSERT":
            name = e.dxf.get("name") or ""
            if role in ("door", "window"):
                door_inserts[role] += 1
            if name not in seen_blocks and name in doc.blocks:
                seen_blocks.add(name)
                blk = doc.blocks[name]
                if role == "window":
                    n = sum(1 for b in blk if b.dxftype() == "LINE")
                    window_block_lines[str(min(n, 9))] += 1
                queue.extend((b, layer) for b in blk)
        elif t in ("TEXT", "MTEXT"):
            text = _plain(e)
            kind = text_kind(text, role)
            if not kind:
                continue
            kinds_layers[kind][layer] += 1
            h = float(e.dxf.get("height", 0) or 0) if t == "TEXT" else float(e.dxf.get("char_height", 0) or 0)
            h = h or styles.get(str(e.dxf.get("style", "")).upper(), 0.0)
            if h > 0:
                heights[kind].append(h)
            if kind == "room_label":
                up = " ".join(text.split())
                labels[fold_ascii(up).upper()] += 1
                spelling["turkish_letters" if set(up) & TR_LETTERS else "ascii_only"] += 1
                case["upper" if up == up.upper() else ("title" if up == up.title() else "mixed")] += 1
            elif kind != "dimension":
                shapes[kind][shape(text)] += 1
            else:
                shapes[kind]["decimal" if re.search(r"[.,]", text) else "integer"] += 1
        elif t == "ARC" and role in ("door", "window"):
            sweep = (float(e.dxf.end_angle) - float(e.dxf.start_angle)) % 360
            arcs.append((float(e.dxf.radius), round(sweep / 5) * 5))
        elif t == "HATCH":
            hatch[f"{role or 'other'}|{e.dxf.get('pattern_name', '')}"] += 1
        elif t == "DIMENSION":
            dims[f"{layer}|{e.dxf.get('dimstyle', '')}"] += 1
    mpu, unit = _units_guess(doc.header.get("$INSUNITS", 0), [r for r, s in arcs if 80 <= s <= 100])
    if mpu_known:
        mpu = float(mpu_known)
        unit = {0.001: "mm", 0.01: "cm", 1.0: "m"}.get(round(mpu, 6), f"1 unit = {mpu:g} m")
    m = mpu or 0.0
    dimtxt = []
    for ds in doc.dimstyles:
        txt, scale = float(ds.dxf.get("dimtxt", 0) or 0), float(ds.dxf.get("dimscale", 1) or 1)
        if txt > 0:
            dimtxt.append(round(txt * scale * m, 3))
    return {"file": Path(path).name, "insunits": doc.header.get("$INSUNITS", 0), "unit": unit, "mpu": mpu,
            "layers": {r: c.top() for r, c in layer_counts.items()},
            "text_layers": {k: c.top(10) for k, c in kinds_layers.items()},
            "text_heights_m": {k: dict(collections.Counter(round(h * m, 3) for h in v).most_common(12))
                               for k, v in heights.items()},
            "shapes": {k: c.top(25) for k, c in shapes.items()},
            "room_labels": labels.top(60), "label_spelling": dict(spelling), "label_case": dict(case),
            "door_arcs": {"radius_m": dict(collections.Counter(round(r * m / 0.05) * 0.05 for r, s in arcs
                                                               if 80 <= s <= 100).most_common(10)),
                          "sweep_deg": dict(collections.Counter(s for _, s in arcs).most_common(6))},
            "door_window_inserts": dict(door_inserts), "window_block_lines": dict(window_block_lines),
            "hatch": hatch.top(20), "dimensions": dims.top(10), "dim_text_m": sorted(set(dimtxt))[:12]}


# --- the profile ----------------------------------------------------------------------------------------------------

def _merge(items: list[dict], top: int = 12, norm=lambda k: k, keep=None) -> dict:
    """``{key: {"share": s, "projects": n}}`` over the per-project counters, the most frequent ``top`` keys (``keep``:
    a filter on the key, e.g. a plausible range of text heights: a block inserted at a scale is not measured)."""
    total, proj = collections.Counter(), collections.Counter()
    for d in items:
        seen = set()
        for k, v in (d or {}).items():
            if keep is not None and not keep(k):
                continue
            k2 = norm(k)
            total[k2] += v
            if k2 not in seen:
                proj[k2] += 1
                seen.add(k2)
    s = sum(total.values()) or 1
    return {str(k): {"share": round(v / s, 4), "projects": proj[k]} for k, v in total.most_common(top)}


def wall_thicknesses(work: Path) -> dict:
    """The wall thicknesses (cm) of the CPU readings ``work/<p>/building.json``, as shares."""
    c = collections.Counter()
    for b in sorted(Path(work).glob("*/building.json")):
        try:
            data = json.loads(b.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for w in data.get("walls") or []:
            t = w.get("thickness")
            if t:
                c[int(round(float(t) * 100))] += 1
    s = sum(c.values()) or 1
    return {str(k): round(v / s, 4) for k, v in c.most_common(15)}


def build(measure_dir: Path, readings: Optional[Path] = None) -> dict:
    ms = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(measure_dir).glob("*.json"))]
    roles = ("wall", "plaster", "structure", "door", "window", "stair", "furniture", "dimension", "text", "hatch",
             "axis", "sanitary")
    prof = {"note": "Statistics measured from the user's converted DXFs (layer names per role, text heights, label "
                    "vocabulary, tag and text shapes with digits folded to 9, door arcs, hatches, dimensions, "
                    "units); no drawing content is kept. share = frequency over all counted items, projects = "
                    "number of projects it occurs in. Built by python -m wenart.datasets.turkish_profile build.",
            "projects": len(ms), "units": dict(collections.Counter(m["unit"] for m in ms)),
            "insunits": dict(collections.Counter(str(m["insunits"]) for m in ms)),
            # xref-bound copies ('<xref>$0$<layer>') carry a file name, not a convention: left out
            "layers": {r: _merge([m["layers"].get(r) for m in ms], 10, keep=lambda k: "$" not in k) for r in roles},
            "text_layers": {k: _merge([m["text_layers"].get(k) for m in ms], 8) for k in TEXT_KINDS},
            "text_heights_m": {k: _merge([m["text_heights_m"].get(k) for m in ms], 8,
                                         keep=lambda h, k=k: 0.05 <= float(h) <= (1.5 if k == "title" else 0.6))
                               for k in TEXT_KINDS},
            "shapes": {k: _merge([m["shapes"].get(k) for m in ms], 15) for k in TEXT_KINDS if k != "room_label"},
            "room_labels": _merge([m["room_labels"] for m in ms], 60),
            "label_spelling": _merge([m["label_spelling"] for m in ms]),
            "label_case": _merge([m["label_case"] for m in ms]),
            "door_arc_radius_m": _merge([m["door_arcs"]["radius_m"] for m in ms], 10,
                                        lambda k: f"{float(k):.2f}", keep=lambda r: 0.5 <= float(r) <= 1.3),
            "door_arc_sweep_deg": _merge([m["door_arcs"]["sweep_deg"] for m in ms], 6),
            "door_window_inserts": _merge([m["door_window_inserts"] for m in ms]),
            "window_block_lines": _merge([m["window_block_lines"] for m in ms]),
            "hatch": _merge([m["hatch"] for m in ms], 15),
            "dimension_layers": _merge([{k.split("|")[0]: v for k, v in m["dimensions"].items()} for m in ms], 10),
            "dimension_text_m": _merge([{str(x): 1 for x in m["dim_text_m"]} for m in ms], 10,
                                       keep=lambda h: 0.05 <= float(h) <= 0.5),
            # not measurable by counting single texts: the converter's own assumptions, stated as such
            "assumed": {"two_text_tag_share": 0.15,
                        "storey_height_m": {"2.85": 0.2, "3.00": 0.5, "3.06": 0.15, "3.20": 0.15},
                        "note": "two-text size tags (width over height as two texts) and storey heights are not "
                                "counted from the drawings; these shares are the converter's assumptions"}}
    if readings:
        prof["wall_thickness_cm"] = wall_thicknesses(readings)
    return prof


def reading_mpu(building_json: Path) -> Optional[float]:
    """The most frequent ``metres_per_unit`` of a CPU reading (the reader's scale of the drawing), else None."""
    try:
        found = re.findall(r'"metres_per_unit": *([0-9.eE+-]+)', Path(building_json).read_text(encoding="utf-8"))
    except OSError:
        return None
    return float(collections.Counter(found).most_common(1)[0][0]) if found else None


def load(path: Path = PROFILE_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[0] == "measure":
        mpu = float(argv[argv.index("--mpu") + 1]) if "--mpu" in argv else None
        out = measure(Path(argv[1]), mpu)
        Path(argv[2]).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        return 0
    if len(argv) >= 2 and argv[0] == "build":
        readings = Path(argv[argv.index("--readings") + 1]) if "--readings" in argv else None
        out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else PROFILE_PATH
        prof = build(Path(argv[1]), readings)
        out.write_text(json.dumps(prof, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"profile: {out} ({prof['projects']} projects)")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
