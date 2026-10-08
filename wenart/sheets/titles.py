"""Title words of drawing regions: class, level and alternative keywords in Turkish, English, German and French
(docs/milestone10.md §3.1 items 2-4).

What: ``class_of(text) -> (class, keywords, language) | None``, ``level_of(text) -> LevelWord | None``,
``alternative_of(text) -> (name, how) | None`` and ``pick_title(region_texts, geometry_box)``.

Why: the region's own title decides its class and level before any geometry or AI (trust order). One table per
language keeps the words in one place; nothing else is matched (an unknown word gives no class, never a guess).

How: texts are ASCII-folded and upper-cased (``wenart.building.fold_ascii``: ``ÇATI KAT PLANI`` -> ``CATI KAT
PLANI``) and matched as whole words, most specific class first (``ÇATI KAT PLANI`` is an attic floor plan, ``ÇATI
PLANI`` a roof plan; ``MOBİLYA PLANI`` a furniture plan before ``KAT PLANI``). The title of a region is its text with
a class or level word (the tallest such text); without one, nothing is a title. Room labels (``SALON 46M2``) carry
no class word and never become titles.
"""
from __future__ import annotations

import re
from typing import Optional

from wenart import building as B
from wenart.sheets.levels import LevelWord, level_of  # noqa: F401 - re-exported

# (class, pattern on the ASCII-folded upper-case text, language), most specific first.
CLASS_WORDS: list[tuple[str, str, str]] = [
    # roof plans before the attic floor plans and before the generic PLAN words
    ("roof_plan", r"\bCATI PLANI\b", "tr"),
    ("roof_plan", r"\bROOF PLAN\b", "en"),
    ("roof_plan", r"\bDACH(?:DR)?AUFSICHT\b", "de"),
    ("roof_plan", r"\bPLAN DE(?:S)? TOITURES?\b", "fr"),
    ("site_plan", r"\bVAZIYET(?: PLANI)?\b", "tr"),
    ("site_plan", r"\bSITE PLAN\b", "en"),
    ("site_plan", r"\bLAGEPLAN\b", "de"),
    ("site_plan", r"\bPLAN DE MASSE\b", "fr"),
    ("site_plan", r"\bPLAN DE SITUATION\b", "fr"),
    ("furniture_plan", r"\bMOBILYA(?: PLANI)?\b", "tr"),
    ("furniture_plan", r"\bFURNITURE (?:LAYOUT )?PLAN\b", "en"),
    ("furniture_plan", r"\bMOEBLIERUNG(?:SPLAN)?\b|\bMOBLIERUNG(?:SPLAN)?\b", "de"),
    ("furniture_plan", r"\bPLAN D'AMEUBLEMENT\b", "fr"),
    ("section", r"\bKESIT(?:I)?\b", "tr"),
    ("section", r"\bSECTION\b", "en"),
    ("section", r"\bSCHNITT\b", "de"),
    ("section", r"\bCOUPE\b", "fr"),
    ("elevation", r"\bGORUNUS(?:U)?\b", "tr"),
    ("elevation", r"\bCEPHE\b", "tr"),
    ("elevation", r"\bELEVATION\b", "en"),
    ("elevation", r"\bANSICHT\b", "de"),
    ("elevation", r"\bFACADE\b", "fr"),
    ("detail", r"\bDETAY\b", "tr"),
    ("detail", r"\bDETAIL\b", "en"),
    ("legend", r"\bLEJANT\b", "tr"),
    ("legend", r"\bLEGEND\b", "en"),
    ("legend", r"\bLEGENDE\b", "de"),
    ("3d_view", r"\bPERSPEKTIF\b", "tr"),
    ("3d_view", r"\bPERSPECTIVE\b", "en"),
    ("3d_view", r"\b3D\b", "en"),
    ("floor_plan", r"\bKAT PLANI\b", "tr"),
    ("floor_plan", r"\bFLOOR PLAN\b", "en"),
    ("floor_plan", r"\bGRUNDRISS\b", "de"),
    ("floor_plan", r"\bPLAN DU\b|\bPLAN D'ETAGE\b", "fr"),
    ("floor_plan", r"\bPLAN\b", "en"),
]
_CLASS_RE = [(cls, re.compile(pat), lang) for cls, pat, lang in CLASS_WORDS]

# Alternative words (§3.1 item 4).
ALTERNATIVE_WORDS = ("ALTERNATIF", "SECENEK", "OPSIYON", "VARYANT", "ALTERNATIVE", "OPTION", "VARIANT", "VARIANTE")
_ALT_RE = re.compile(r"\b(" + "|".join(ALTERNATIVE_WORDS) + r")\b\s*[:\-]?\s*(.*)$")
_BRACKET_RE = re.compile(r"[\(\[]\s*([^\)\]]*?)\s*[\)\]]")

# English glosses of alternative names (ASCII-folded lower case keys).
GLOSS = {
    "acik mutfak": "open kitchen",
    "kapali mutfak": "closed kitchen",
    "amerikan mutfak": "open kitchen",
    "acik plan": "open plan",
    "acik salon": "open living room",
    "ek oda": "extra room",
    "ofis": "office",
    "calisma odasi": "study",
    "stüdyo": "studio",
    "studyo": "studio",
    "dubleks": "duplex",
}


def fold(text: str) -> str:
    return " ".join(B.fold_ascii(text).upper().split())


def class_of(text: str) -> Optional[tuple[str, list[str], str]]:
    """(class, matched words, language) of a title text, or None."""
    folded = fold(text)
    for cls, pattern, lang in _CLASS_RE:
        m = pattern.search(folded)
        if m:
            if cls == "roof_plan" and re.search(r"\bCATI KAT", folded):
                continue                          # ÇATI KAT PLANI: the attic floor plan, not a roof plan
            words = [m.group(0)]
            level = level_of(text)
            if level is not None:
                words.insert(0, level.word)
            return cls, words, lang
    return None


def alternative_of(text: str) -> Optional[tuple[str, str]]:
    """(name as titled, how: word | bracket) of an alternative plan title, or None for a base title.

    ``BODRUM KAT PLANI BRÜT 92 M2 ( Açık mutfak)`` -> (``Açık mutfak``, ``bracket``); ``ZEMİN KAT PLANI
    ALTERNATİF 2`` -> (``2``, ``word``); a bracket holding only an area or a scale (``(92 m²)``, ``(1/100)``) is no
    alternative."""
    folded = fold(text)
    m = _ALT_RE.search(folded)
    if m:
        start = m.start(2)
        name = _original_slice(text, folded, start).strip(" :-()[]") or m.group(1).title()
        return name, "word"
    for bm in _BRACKET_RE.finditer(text):
        inner = bm.group(1).strip()
        if not inner or re.fullmatch(r"[\d\s.,/:]*(m2|m²|sq ?ft)?", inner, re.IGNORECASE):
            continue
        return inner, "bracket"
    return None


def _original_slice(text: str, folded: str, start: int) -> str:
    """The part of the original text from the word at ``start`` of its folded form (same word count)."""
    words_before = len(folded[:start].split())
    return " ".join(text.split()[words_before:])


def slug(name: str) -> str:
    """ASCII slug of an alternative name: ``Açık mutfak`` -> ``acik-mutfak``."""
    s = re.sub(r"[^a-z0-9]+", "-", B.fold_ascii(name).lower()).strip("-")
    return s or "alt"


def gloss(name: str) -> Optional[str]:
    return GLOSS.get(" ".join(B.fold_ascii(name).lower().split()))


def language_of(text: str) -> Optional[str]:
    hit = class_of(text)
    if hit:
        return hit[2]
    level = level_of(text)
    return level.language if level else None


def pick_title(texts, geometry_box, region_height: Optional[float] = None):
    """The region's title: among its texts with a class or level word, the tallest (ties: the lowest, then the
    leftmost). Texts inside the drawing count only when they are clearly larger than its labels (>= 2 x the median
    text height); below or above the drawing (within 0.3 x its height) any keyword text counts."""
    import statistics

    if not texts:
        return None
    median_h = statistics.median(t.height for t in texts) if texts else 0.0
    h = region_height if region_height is not None else (geometry_box[3] - geometry_box[1])
    cands = []
    for t in texts:
        if class_of(t.text) is None and level_of(t.text) is None:
            continue
        p = t.point
        outside = p[1] < geometry_box[1] or p[1] > geometry_box[3] or p[0] < geometry_box[0] or p[0] > geometry_box[2]
        near = (geometry_box[1] - 0.3 * h - t.height <= p[1] <= geometry_box[3] + 0.3 * h + t.height)
        if outside and near or (not outside and t.height >= 2.0 * median_h) or len(texts) == 1:
            cands.append(t)
    if not cands:
        # A drawing whose only keyword text sits inside it at label size (a synthetic title inside the frame).
        cands = [t for t in texts if class_of(t.text) is not None]
    if not cands:
        return None
    return max(cands, key=lambda t: (t.height, -t.point[1], -t.point[0]))
