"""The building's storeys from the drawing's unused block definitions (20 Nov 2026; pre-pod review R03-01: real03's
tekkat.dwg inserts only the ground-floor plan 'D BLOK_ZK' in model space, but defines, unused, the whole D Blok: the
plans 'D BLOK_BK', 'D BLOK_1K', 'D BLOK_NK' ..., the sections 'D BLOK KESİTLER' and elevations 'D BLOK GÖRÜNÜŞLER' with
marks every 3.20 m, and a building-info block 'XX_BİNA BİLGİLERİ': 'D BLOK / 1BK+ZK+12K / ... BİNA GİRİŞ KOTU : 93.20',
whose entrance level is the plan's own datum mark).

What: ``read(path, plan_values) -> Optional[dict]``: ``{"count", "basements", "pitch_m", "basement_floors_m", "text",
"evidence", "note"}`` from a DXF's block definitions, or None. A building-info text counts only when its entrance level
(BİNA GİRİŞ KOTU) equals a value printed on the drawn plan (``plan_values``: the plan's datum mark) and it names the
inserted plan's building (the block name's prefix, 'D BLOK') or is the only such text; its storeys are read in the
'nBK+ZK+mK' form (n basements, the ground floor and m floors above). The storey pitch comes from the level marks of the
unused section and elevation blocks that share the inserted plan block's name prefix ('D BLOK_ZK' -> 'D BLOK ...'): the
step that most of their consecutive marks rise by, within 2.2-4.5 m (at least three times); the basements' floors walk
down from 0.00 by such steps. It is a lower-trust rung of the storey ladder (logged inferred, the block names as
evidence).

How: ezdxf on the converted DXF, read only when the raw file holds an entrance-level word (``PREFILTER_RE``) and the
storey ladder has no count from the drawn documents; no project data.
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Optional

INFO_LEVEL_RE = re.compile(r"(?:BINA\s+)?GIRIS\s+KOTU\s*[:=]?\s*(\d{1,4}[.,]\d{1,2})"
                           r"|ENTRANCE\s+LEVEL\s*[:=]?\s*(\d{1,4}[.,]\d{1,2})")
STOREYS_RE = re.compile(r"(?<![A-Z0-9])(?:(\d)\s*BK?\s*\+\s*)?(?:ZK|Z|ZEMIN|G)\s*\+\s*(\d{1,2})\s*(?:K|NK|KAT)?"
                        r"(?![A-Z0-9])")
MARK_RE = re.compile(r"(?<![\d.,])([+\-±]?)\s*(\d{1,3}[.,]\d{2})(?![\d])")
PITCH_M = (2.2, 4.5)
PITCH_MIN_STEPS = 3
SECTION_WORDS = ("KESIT", "GORUNUS", "SECTION", "ELEVATION", "SCHNITT", "ANSICHT", "COUPE", "FACADE")
# the raw file holds an entrance-level text (KOTU in UTF-8 or next to the DXF's \U+ escapes of the dotted capitals)
PREFILTER_RE = re.compile(rb"(?i)KOTU|ENTRANCE\s+LEVEL")


def _fold(text) -> str:
    from wenart import building as B
    return " ".join(B.fold_ascii(str(text or "")).upper().split())


def _texts(block) -> list[str]:
    out = []
    for e in block:
        t = e.dxftype()
        try:
            if t == "TEXT":
                out.append(e.dxf.text)
            elif t == "MTEXT":
                out.append(e.plain_text())
            elif t == "INSERT":
                out += [a.dxf.text for a in e.attribs]
            elif t == "ATTDEF":
                out.append(e.dxf.text)
        except Exception:  # noqa: BLE001 - a broken entity is skipped
            continue
    return [x for x in out if x]


def _used(doc) -> set:
    used, todo = set(), [doc.modelspace()]
    while todo:
        space = todo.pop()
        for e in space:
            if e.dxftype() == "INSERT":
                name = e.dxf.name
                if name not in used and name in doc.blocks:
                    used.add(name)
                    todo.append(doc.blocks[name])
    return used


def _num(s: str) -> float:
    return float(s.replace(",", "."))


def basement_floors(vals: list, basements: int) -> list:
    """The basements' floor marks, walking down from 0.00 (pure): each the highest mark at least ``PITCH_M[0]`` and at
    most ``PITCH_M[1]`` below the floor above (real03's section: -4.00, the 1st basement; -5.00 below it is no storey)."""
    out, top = [], 0.0
    for _k in range(basements):
        below = [v for v in vals if top - PITCH_M[1] - 1e-6 <= v <= top - PITCH_M[0] + 1e-6]
        if not below:
            break
        top = max(below)
        out.append(round(top, 2))
    return out


def pitch_of(vals: list) -> Optional[float]:
    """The step most consecutive marks rise by within ``PITCH_M``, seen at least ``PITCH_MIN_STEPS`` times (pure)."""
    vals = sorted(set(vals))
    steps = Counter(round(b - a, 2) for a, b in zip(vals, vals[1:]) if PITCH_M[0] <= b - a <= PITCH_M[1])
    if not steps or steps.most_common(1)[0][1] < PITCH_MIN_STEPS:
        return None
    return steps.most_common(1)[0][0]


def read(path, plan_values: set) -> Optional[dict]:
    """The module docstring."""
    import ezdxf
    from ezdxf import recover

    p = Path(path)
    if p.suffix.lower() != ".dxf" or not p.is_file():
        return None
    try:
        if not PREFILTER_RE.search(p.read_bytes()):
            return None                     # no entrance-level text anywhere in the file: nothing to read
    except OSError:
        return None
    try:
        doc = ezdxf.readfile(str(p))
    except Exception:  # noqa: BLE001 - a damaged file: the recover reader
        try:
            doc, _aud = recover.readfile(str(p))
        except Exception:  # noqa: BLE001
            return None
    used = _used(doc)
    model_inserts = {e.dxf.name for e in doc.modelspace() if e.dxftype() == "INSERT"}
    prefixes = {n.rsplit("_", 1)[0].strip() for n in model_inserts if "_" in n and len(n.rsplit("_", 1)[0].strip()) >= 3}
    folded_px = {_fold(px) for px in prefixes}
    cands = []
    for blk in doc.blocks:
        if blk.name.startswith("*"):
            continue
        for text in _texts(blk):
            f = _fold(text)
            m = INFO_LEVEL_RE.search(f)
            s = STOREYS_RE.search(f) if m else None
            level = _num(m.group(1) or m.group(2)) if m else None
            if s and round(level, 2) in plan_values:
                cands.append((blk.name, text, int(s.group(1) or 0), int(s.group(2)), level,
                              any(px and px in f for px in folded_px)))
    # the text names the inserted plan's building ('D BLOK'), or is the only one with the plan's entrance level
    named = [c for c in cands if c[5]]
    pick = named if named else (cands if len(cands) == 1 else [])
    if not pick or len({(c[2], c[3]) for c in pick}) > 1:
        return None
    name, info_text, basements, above, level, _named = pick[0]
    marks, ev = [], [{"rule": "dwg_building_info", "block": name, "text": " ".join(info_text.split())[:160]}]
    for blk in doc.blocks:
        if blk.name in used or blk.name.startswith("*") or not any(blk.name.startswith(px) for px in prefixes):
            continue
        if not any(w in _fold(blk.name) for w in SECTION_WORDS):
            continue
        vals = set()
        for text in _texts(blk):
            for sign, v in MARK_RE.findall(_fold(text)):
                x = _num(v) * (-1.0 if sign == "-" else 1.0)
                if abs(x) < 200:
                    vals.add(round(x, 2))
        if len(vals) >= 3:
            marks += sorted(vals)
            ev.append({"rule": "dwg_section_marks", "block": blk.name, "text": f"{len(vals)} level marks"})
    pitch = pitch_of(marks)
    floors = basement_floors(sorted(set(marks)), basements) if pitch else []
    short = " ".join(info_text.split())[:80]
    note = (f"the drawing's unused block '{name}' gives {basements} basement(s), the ground floor and {above} floor(s) "
            f"above ('{short}'), its entrance level {level:.2f} the plan's own mark"
            + (f"; the unused section and elevation blocks step {pitch:.2f} m a storey" if pitch else ""))
    return {"count": above + 1, "basements": basements, "pitch_m": pitch, "basement_floors_m": floors,
            "text": short, "evidence": ev[:4], "note": note}
