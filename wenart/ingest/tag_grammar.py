"""One size-tag grammar for the whole pipeline (27 Nov 2026, audit fix round 5a, rule R09).

What: ``parse(text, layer=None) -> SizeTag | None`` reads a door or window size tag as the drawings write it: an
optional code (one to three letters and up to two digits, then '-', ':', '.', '=' or a space: 'CK3 350/220',
'K3-100/210', 'P2:60/60', 'K 100/210', 'K1: 90/210'), the width and the height in cm ('70/150') and optional trailing
words ('180/210 FRANSIZ PENCERE', '200/210 SÜRGÜ KAPI', 'PORTE-FENÊTRE', 'French window'). It returns the width, the
height, the code, the kind the code or the words name (``door``, ``window``, ``french_window`` or None when the tag does
not say), the operation they name (``sliding``, ``folding`` or None) and whether they say glass.

A code whose type number runs straight into the width (28 Nov 2026, round 5a fix-up TAGS-1: real14's POZ layer writes
'K290/210', 'K180/210', 'P150/50' beside 'K2100/210' and 'P3130/150'): a glued 4- or 5-digit group is the type number
and a 3-digit width ('K2100' = K2 + 100, 'P3130' = P3 + 130); a glued 3-digit group reads both ways: the type number
and a 2-digit width first ('K290' = K2 + 90, the old readers' reading), the 3-digit width as ``w_alt_cm`` ('K290' =
2.90 m). ``glued_convention(texts)`` decides per drawing: a glued 4- or 5-digit group among its texts proves the
type-number convention and ``parse(text, convention=...)`` then reads the 3-digit group one way only. An ambiguous tag
never sets a width alone: a reader takes the reading an opening's own width agrees with (``pick``) or leaves the width
as read.

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
from dataclasses import dataclass, replace
from typing import Optional

from wenart.textfold import fold_ascii

# the code: 1-3 letters, then its type number (1-2 digits) and a separator ('-', ':', '.', '=' or a space), or a
# separator alone, or the digits glued to the width (``run``: 'K290', 'K2100', read by ``_glued``)
TAG_RE = re.compile(r"^\s*(?:(?P<code>[A-Z]{1,3})(?P<gap>\s*)"
                    r"(?:(?P<num>\d{1,2})(?:\s*(?P<sep>[-:.=])\s*|\s+)|(?P<sep0>[-:.=])\s*)?)?"
                    r"(?P<run>\d{2,5})\s*/\s*(?P<h>\d{2,3})"
                    r"(?P<words>(?:\s+[A-Z][A-Z0-9 .'\-]*)?)\s*$")
GLUED_MIN_W_CM = 30             # a glued 3-digit group reads as type number + width when its last two digits are this
GLUED_MAX_W_CM = 600            # ... and as one width when it is at most this
TYPE_WORDS = ("TIP", "TYPE", "TYP", "TUR", "TURU")    # 'TİP A', 'TÜR B': a type note, it names no door or window
FORMULA_CODES = ("R", "RH", "H", "G", "N")
# kind from the code (first match wins): door codes (kapı, door, cam kapı, sürgü kapı, balkon kapısı), window codes
DOOR_CODES = ("K", "KP", "CK", "SK", "DK", "GK", "YK", "BK", "PK", "AK", "D", "DR", "T")
WINDOW_CODES = ("P", "W", "F", "CP", "SP", "V", "PN", "PE")
GLAZED_CODES = ("CK", "CP")
SLIDING_CODES = ("SK", "SP")
# kind and operation from the trailing words
FRENCH_WORDS = ("FRANSIZ", "FRENCH", "PORTE-FENETRE", "PORTEFENETRE", "FENETRE-PORTE", "BALKONTUR")
WINDOW_WORDS = ("PENCERE", "PENCERESI", "WINDOW", "FENSTER", "FENETRE", "VITRIN", "VITRINE")
DOOR_WORDS = ("KAPI", "KAPISI", "DOOR", "PORTE")     # never TUR: the Turkish TÜR is a type (TAGS-9)
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
    w_alt_cm: Optional[int] = None    # a glued 3-digit group's other reading ('K290/210': 90 cm, alt 290 cm; TAGS-1)

    @property
    def w(self) -> float:
        return self.w_cm / 100.0

    @property
    def h(self) -> float:
        return self.h_cm / 100.0

    @property
    def ambiguous(self) -> bool:
        """A glued 3-digit group the drawing does not decide: the width reads two ways (``w_alt_cm``)."""
        return self.w_alt_cm is not None

    @property
    def widths(self) -> tuple:
        """The width readings in m: the first reading, then the other one of an ambiguous tag."""
        return (self.w,) + ((self.w_alt_cm / 100.0,) if self.w_alt_cm is not None else ())

    def pick(self, width_m, tol: Optional[float] = None) -> Optional["SizeTag"]:
        """The tag read with the width reading nearest ``width_m`` (an opening's own width), one way only; None when
        ``tol`` is given and no reading is within it."""
        try:
            ref = float(width_m)
        except (TypeError, ValueError):
            return None if self.ambiguous else self
        best = min(self.widths, key=lambda w: abs(w - ref))
        if tol is not None and abs(best - ref) > tol:
            return None
        if not self.ambiguous:
            return self
        return replace(self, w_cm=int(round(best * 100)), w_alt_cm=None)

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
        out = {"text": self.text, "w": self.w, "h": self.h, "code": self.code + self.number, "kind": self.kind,
               "operation": self.operation, "glazed": self.glazed, "words": self.words}
        if self.w_alt_cm is not None:
            out["w_alt"] = self.w_alt_cm / 100.0
        return out


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


def _glued(run: str, coded: bool, glued: bool, convention: Optional[str]):
    """``(number, width_cm, alt_cm)`` of the digits before '/' (module docstring, TAGS-1), or None: not a tag."""
    if len(run) == 2:
        return "", int(run), None
    if len(run) == 3:
        if not glued or run[1] == "0" or int(run[1:]) < GLUED_MIN_W_CM:
            return "", int(run), None
        alt = int(run) if int(run) <= GLUED_MAX_W_CM and convention != "type_number" else None
        return run[0], int(run[1:]), alt
    if not coded:
        return None                         # '2100/210' is no tag
    num, w = (run[:2], run[2:]) if len(run) == 5 or run[1] == "0" else (run[:1], run[1:])
    return (num, int(w), None) if int(w) >= GLUED_MIN_W_CM else None


def parse(text, layer=None, convention: Optional[str] = None) -> Optional[SizeTag]:
    """The size tag ``text`` writes (module docstring), or None (pure). ``layer``: the text's layer; a text on a
    dimension or axis layer is never a tag. ``convention``: the drawing's (``glued_convention``); 'type_number' reads a
    glued 3-digit group as the type number and a 2-digit width only."""
    up = _fold(text)
    if not up or "/" not in up or _layer_skipped(layer) or is_formula(up):
        return None
    m = TAG_RE.match(up)
    if not m:
        return None
    code, num = (m.group("code") or ""), (m.group("num") or "")
    if code in FORMULA_CODES:
        return None
    sep = m.group("sep") or m.group("sep0")
    if sep == "=" and code not in DOOR_CODES + WINDOW_CODES:
        return None
    run = m.group("run")
    if num and len(run) > 3:
        return None
    if num:
        got = ("", int(run), None)
    else:
        got = _glued(run, bool(code), bool(code) and not sep and not m.group("gap"), convention)
    if got is None:
        return None
    num = num or got[0]
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
    typed = bool(words) and words.split()[0] in TYPE_WORDS and len(words.split()) <= 2
    if words and kind is None and operation is None and not glazed and not typed:
        return None                         # words that name no door or window: not a size tag ('120/90 TEZGAH')
    return SizeTag(text=str(text).strip(), w_cm=got[1], h_cm=int(m.group("h")), code=code, number=num,
                   kind=kind, operation=operation, glazed=glazed, words=words, w_alt_cm=got[2])


def _text_of(t) -> str:
    if isinstance(t, dict):
        return str(t.get("text") or "")
    return str(getattr(t, "text", t) or "")


def glued_convention(texts) -> Optional[str]:
    """'type_number' when a text of the drawing glues a type number to a 3-digit width ('K2100/210', 'P3130/150'):
    its glued 3-digit groups ('K290/210') are the type number and a 2-digit width; else None (pure; TAGS-1)."""
    for t in texts or []:
        up = _fold(_text_of(t))
        if "/" not in up or not up[:1].isalpha():
            continue
        m = TAG_RE.match(up)
        if m and m.group("code") and not m.group("num") and not (m.group("sep") or m.group("sep0")) \
                and len(m.group("run")) >= 4 and parse(up) is not None:
            return "type_number"
    return None


def size_cm(text, layer=None, convention: Optional[str] = None) -> Optional[tuple[int, int]]:
    """``(width, height)`` in cm of the tag ``text`` writes (the first reading of an ambiguous one), or None (pure)."""
    t = parse(text, layer, convention)
    return (t.w_cm, t.h_cm) if t else None


def door_size(text, min_h_cm: int = DOOR_HIGH_CM, layer=None, convention: Optional[str] = None) -> Optional[SizeTag]:
    """The tag when it can be a door's: its code or words do not say window, and it is at least ``min_h_cm`` high
    (pure)."""
    t = parse(text, layer, convention)
    if t is None or t.says_window or t.h_cm < min_h_cm:
        return None
    return t


def window_size(text, layer=None, convention: Optional[str] = None) -> Optional[SizeTag]:
    """The tag when it can be a window's: its code or words do not say door (pure)."""
    t = parse(text, layer, convention)
    return None if t is None or t.says_door else t


def says_window(text, layer=None) -> bool:
    """The text is a size tag whose code or words say window ('P:120/150', '180/210 FRANSIZ PENCERE') (pure)."""
    t = parse(text, layer)
    return t is not None and t.says_window


def says_door(text, layer=None) -> bool:
    """The text is a size tag whose code or words say door ('K3-100/210', 'CK3 260/240', '200/210 SÜRGÜ KAPI')."""
    t = parse(text, layer)
    return t is not None and t.says_door
