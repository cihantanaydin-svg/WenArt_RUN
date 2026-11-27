"""One size-tag grammar for the whole pipeline (27 Nov 2026, audit fix round 5a, rule R09).

What: ``parse(text, layer=None) -> SizeTag | None`` reads a door or window size tag as the drawings write it: an
optional code (one to three letters and up to two digits, then '-', ':', '.', '=' or a space: 'CK3 350/220',
'K3-100/210', 'P2:60/60', 'K 100/210', 'K1: 90/210'), the width and the height in cm ('70/150') and optional trailing
words ('180/210 FRANSIZ PENCERE', '200/210 SÜRGÜ KAPI', 'PORTE-FENÊTRE', 'French window'). It returns the width, the
height, the code, the kind the code or the words name (``door``, ``window``, ``french_window`` or None when the tag does
not say), the operation they name (``sliding``, ``folding`` or None) and whether they say glass. ``pair_text`` turns a
width and a height written as two texts (``core.paired_size_tags``) into one tag text.

Not tags: stair formulas ('(19X17.36Rh=330/27)', '17x17.64Rh=300/27': ``stair_formula.FORMULA_RE`` and every text with
'Rh', 'H=' or brackets; they go to the stair reader, R24), texts on a dimension or axis layer, numbers of one digit
('1/50' is a scale) and codes of the formula letters (R, RH, H, G, N).

Why: about fourteen regular expressions read size tags, each with its own prefix rule; three of them rejected
'CK3 350/220' and 'K3-100/210' and none accepted '180/210 FRANSIZ PENCERE' (real15's glass doors built as windows,
real17's French windows built as pairs of small windows, real06's 'K3-100/210' entrance door). Every reader of the
pipeline now asks this module and decides by the kind it returns.

How: pure text parsing on ``textfold.fold_ascii`` text, upper case; the layer's role from ``layer_names``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from wenart.textfold import fold_ascii

# the code: 1-3 letters, up to 2 digits (lazy: 'K290/210' is 290/210, never K2 + 90/210), one separator
TAG_RE = re.compile(r"^\s*(?:(?P<code>[A-Z]{1,3})\s*(?P<num>\d{0,2}?)\s*(?P<sep>[-:.=])?\s*)?"
                    r"(?P<w>\d{2,3})\s*/\s*(?P<h>\d{2,3})"
                    r"(?P<words>(?:\s+[A-Z][A-Z .'\-]*)?)\s*$")
FORMULA_CODES = ("R", "RH", "H", "G", "N")
# kind from the code (first match wins): door codes (kapı, door, cam kapı, sürgü kapı, balkon kapısı), window codes
DOOR_CODES = ("K", "KP", "CK", "SK", "DK", "GK", "YK", "BK", "PK", "AK", "D", "DR", "T")
WINDOW_CODES = ("P", "W", "F", "CP", "SP", "V", "PN", "PE")
GLAZED_CODES = ("CK", "CP")
SLIDING_CODES = ("SK", "SP")
# kind and operation from the trailing words
FRENCH_WORDS = ("FRANSIZ", "FRENCH", "PORTE-FENETRE", "PORTEFENETRE", "FENETRE-PORTE", "BALKONTUR")
WINDOW_WORDS = ("PENCERE", "PENCERESI", "WINDOW", "FENSTER", "FENETRE", "VITRIN", "VITRINE")
DOOR_WORDS = ("KAPI", "KAPISI", "DOOR", "TUR", "TURE", "PORTE")
SLIDING_WORDS = ("SURGU", "SURGULU", "SLIDING", "SCHIEBE", "SCHIEBETUR", "COULISSANTE")
FOLDING_WORDS = ("KATLANIR", "FOLDING", "FALT", "FALTTUR")
GLASS_WORDS = ("CAM", "CAMLI", "GLASS", "GLAZED", "GLAS", "VITRE")
NOT_TAG_ROLES = ("dimension", "axis")
DOOR_HIGH_CM = 180              # a tag this high names a door's size when its code and words do not say
FULL_HEIGHT_CM = 200            # a window tag this high is floor-level glass (a French window)


@dataclass(frozen=True)
class SizeTag:
    text: str                   # the text as written (stripped)
    w_cm: int
    h_cm: int
    code: str = ""              # the letters of the code ('', 'K', 'CK', 'P')
    number: str = ""            # the digits after them ('', '3')
    kind: Optional[str] = None  # 'door' | 'window' | 'french_window' | None (the tag does not say)
    operation: Optional[str] = None   # 'sliding' | 'folding' | None
    glazed: bool = False
    words: str = ""             # the trailing words, folded upper case

    @property
    def w(self) -> float:
        return self.w_cm / 100.0

    @property
    def h(self) -> float:
        return self.h_cm / 100.0

    @property
    def bare(self) -> bool:
        """No code and no words: a plain 'W/H'."""
        return not self.code and not self.words

    @property
    def says_door(self) -> bool:
        return self.kind == "door"

    @property
    def says_window(self) -> bool:
        return self.kind in ("window", "french_window")

    @property
    def floor_level(self) -> bool:
        """Floor-level glass: a French window by its words, or a window or door tag this high (``FULL_HEIGHT_CM``)."""
        return self.kind == "french_window" or self.h_cm >= FULL_HEIGHT_CM

    def as_dict(self) -> dict:
        return {"text": self.text, "w": self.w, "h": self.h, "code": self.code + self.number, "kind": self.kind,
                "operation": self.operation, "glazed": self.glazed, "words": self.words}


def _fold(text) -> str:
    return " ".join(fold_ascii(str(text or "")).upper().split())


def is_formula(text) -> bool:
    """A stair formula or a text of one ('19X17.36Rh=330/27', 'Rh=330/27', '(17x 17.65 / 28)') (pure)."""
    from wenart.ingest.generic import stair_formula as SF

    up = _fold(text)
    if not up:
        return False
    if "(" in up or ")" in up or re.search(r"(?<![A-Z])R\s*H?\s*[=:]|(?<![A-Z])H\s*=", up):
        return True
    return SF.FORMULA_RE.search(up) is not None and SF.parse(up) is not None


def _layer_skipped(layer) -> bool:
    if not layer:
        return False
    from wenart.ingest.generic import layer_names as LN

    return LN.layer_role(layer) in NOT_TAG_ROLES


def parse(text, layer=None) -> Optional[SizeTag]:
    """The size tag ``text`` writes (module docstring), or None (pure). ``layer``: the text's layer; a text on a
    dimension or axis layer is never a tag."""
    up = _fold(text)
    if not up or "/" not in up or _layer_skipped(layer) or is_formula(up):
        return None
    m = TAG_RE.match(up)
    if not m:
        return None
    code, num = (m.group("code") or ""), (m.group("num") or "")
    if code in FORMULA_CODES:
        return None
    if m.group("sep") == "=" and code not in DOOR_CODES + WINDOW_CODES:
        return None
    words = " ".join(m.group("words").split())
    toks = set(words.replace("-", " ").split()) | ({words.replace(" ", "")} if words else set())
    kind = operation = None
    glazed = code in GLAZED_CODES
    if code in DOOR_CODES:
        kind = "door"
    elif code in WINDOW_CODES:
        kind = "window"
    if code in SLIDING_CODES:
        operation = "sliding"
    if toks & set(FRENCH_WORDS) or ("PORTE" in toks and "FENETRE" in toks):
        kind, glazed = "french_window", True
    elif toks & set(DOOR_WORDS):
        kind = "door"
    elif toks & set(WINDOW_WORDS):
        kind = "window"
    if toks & set(SLIDING_WORDS):
        operation = "sliding"
    elif toks & set(FOLDING_WORDS):
        operation = "folding"
    if toks & set(GLASS_WORDS):
        glazed = True
    if words and kind is None and operation is None and not glazed:
        return None                         # words that name no door or window: not a size tag ('120/90 TEZGAH')
    return SizeTag(text=str(text).strip(), w_cm=int(m.group("w")), h_cm=int(m.group("h")), code=code, number=num,
                   kind=kind, operation=operation, glazed=glazed, words=words)


def size_cm(text, layer=None) -> Optional[tuple[int, int]]:
    """``(width, height)`` in cm of the tag ``text`` writes, or None (pure)."""
    t = parse(text, layer)
    return (t.w_cm, t.h_cm) if t else None


def door_size(text, min_h_cm: int = DOOR_HIGH_CM, layer=None) -> Optional[SizeTag]:
    """The tag when it can be a door's: its code or words do not say window, and it is at least ``min_h_cm`` high
    (pure)."""
    t = parse(text, layer)
    if t is None or t.says_window or t.h_cm < min_h_cm:
        return None
    return t


def window_size(text, layer=None) -> Optional[SizeTag]:
    """The tag when it can be a window's: its code or words do not say door (pure)."""
    t = parse(text, layer)
    return None if t is None or t.says_door else t


def says_window(text, layer=None) -> bool:
    """The text is a size tag whose code or words say window ('P:120/150', '180/210 FRANSIZ PENCERE') (pure)."""
    t = parse(text, layer)
    return t is not None and t.says_window


def says_door(text, layer=None) -> bool:
    """The text is a size tag whose code or words say door ('K3-100/210', 'CK3 260/240', '200/210 SÜRGÜ KAPI')."""
    t = parse(text, layer)
    return t is not None and t.says_door


def pair_text(w_cm: int, h_cm: int) -> str:
    """The tag text of a width and a height written as two texts."""
    return f"{int(w_cm)}/{int(h_cm)}"
