"""Level marks (KOT) in every form the drawings use (docs/milestone12.md §3.1, contract §13.2; owner: track L).

Contract (frozen 10 Oct 2026):

- ``parse_mark(text: str) -> dict | None``: one text or attribute value -> ``{"value": float, "relative": bool,
  "absolute": float | None, "kind_hint": str | None, "raw": str}`` or None when it is no level mark. ``kind_hint``
  comes from the keyword (``floor``, ``slab_top``, ``ground_natural``, ``ground_finished``, ``plinth``, ``entrance``,
  ``slope_top``, ``datum``) or None. Pure, no I/O. Track R uses it to keep marks out of the furniture.
- ``MARK_ATTRIBUTE_TAGS``: block attribute tags that hold level marks (``KOT``, ``KOT2``, ``KOT-BINA``, ...).

What: one tolerant reader for the Turkish and English forms: ``±0.00``, ``+-0.00``, ``%%p0.00`` (the DXF code of
±), ``+-0.00(dük)``, ``+0.15``, ``-0.45``, ``KOT +3.00``, ``KOT: +0.15``, ``Ü.K. +0.15``, ``S.K. +3.00``,
``T.Z. -0.45``, ``TABİİ ZEMİN -0.60``, ``TESVİYE 0.00 KOTU : 93.20``, ``SB. KOTU : 93.20``, ``BİNA GİRİŞ KOTU :
93.20``, ``100.18(şev üst kotu)``, ``±0.00 = 93.20``, ``±0.00 KOT``, ``FFL +0.15``. A value has 2 or 3 decimals.

Why: real03 holds about 280 level marks (attributes KOT, KOT2, KOT-BINA, KOT-ARAZI and a site note with 93.20 m)
and the one pattern of Milestone 10 read none of them (bug B10, §1.5). A dimension or an area label must never be
read as a mark (§10 "level marks misread").

How:

- the text is folded to ASCII upper case (``wenart.building.fold_ascii``), ``+-`` / ``+/-`` / ``%%p`` become ``±``;
  a short note in brackets (``(dük)``, ``(şev üst kotu)``) is set apart; then the numbers (sign, 1-4 digits, 2-3
  decimals, ``.`` or ``,``) and the keywords are taken out; anything else left (a word, ``M2``) means no mark;
- a mark needs a sign (``+``, ``-``, ``±``), a keyword (``KOT``, ``Ü.K.``, ``T.Z.`` ...), or, through
  ``read_mark(text, bare=True)``, an attribute tag of ``MARK_ATTRIBUTE_TAGS`` or a mark symbol next to it (the
  caller knows those); a bare ``3.20`` or ``12,50 m²`` is no mark;
- relative or absolute: a signed value or ``0.00`` is relative to ±0.00; an unsigned value of 10 m or more is an
  absolute level (``93.20``); an unsigned value under 10 m is relative (the usual drawings sign every relative
  mark; documented assumption). Two numbers (``±0.00 = 93.20``, ``TESVİYE 0.00 KOTU : 93.20``, ``+0.00 / 93.20``)
  are a relative value with its absolute level: ``value`` is the relative one, ``absolute`` the other (the pair
  gives the datum ``absolute - value``);
- ``kind_hint`` from the keyword table ``KIND_KEYWORDS`` (first match in its order); ``±0.00 = 93.20`` alone is
  ``datum``; ``note`` is true for a written statement (``... KOTU : 93.20``: a site note whose position is not the
  point it marks).

``read_mark`` returns the same record plus ``note`` and ``bare`` (true when only the caller's tag or symbol makes
it a mark).
"""
from __future__ import annotations

import re
from typing import Optional

from wenart import building as B

MARK_ATTRIBUTE_TAGS: tuple[str, ...] = ("KOT", "KOT2", "KOT-BINA", "KOT-ARAZI", "BDK", "TZK", "SBK", "ELEV", "LEVEL")
# What an attribute tag says about the mark (None: its position decides; docs/milestone12.md §3.1).
TAG_KIND = {"KOT-ARAZI": "ground_natural", "TZK": "ground_natural", "BDK": "floor", "SBK": "plinth"}
KINDS = ("floor", "slab_top", "ground_natural", "ground_finished", "plinth", "entrance", "threshold", "slope_top",
         "datum", "unknown")
ABSOLUTE_FROM_M = 10.0          # an unsigned value from 10 m on is an absolute level (93.20, 43.00)
_STOP = r"(?=$|[\s:=/+\-±\d(])"
# (kind, pattern) on the folded upper-case text, first match wins; ``None``: a mark keyword without a kind.
KIND_KEYWORDS: tuple[tuple[Optional[str], re.Pattern], ...] = (
    ("ground_natural", re.compile(r"TABII\s+ZEMIN|\bARAZI\b|\bNGL\b|(?<![A-Z.])T\.?\s?Z\.?" + _STOP)),
    ("ground_finished", re.compile(r"\bTESVIYE\b|\bFGL\b|(?<![A-Z.])GL" + _STOP)),
    ("plinth", re.compile(r"\bSUBASMAN\b|\bSBK\b|(?<![A-Z.])S\.?\s?B\." )),
    ("entrance", re.compile(r"\b(?:BINA\s+)?GIRIS\b")),
    ("slope_top", re.compile(r"\bSEV\s+UST\b")),
    ("slab_top", re.compile(r"\bSSL\b|\bTOS\b|(?<![A-Z.])U\.?\s?K\.?" + _STOP)),
    ("floor", re.compile(r"\bFFL\b|(?<![A-Z.])B\.?\s?D\.?\s?K\.?" + _STOP + r"|(?<![A-Z.])D\.\s?K\." + r"|\bDOSEME\b")),
    (None, re.compile(r"\bKOT(?:U|LARI)?\b|(?<![A-Z.])S\.\s?K\.|\bSK\b|\bELEV\.?\b|\bEL\.|\bLEVEL\b")),
)
_NUM = re.compile(r"(?<![\d.,])([±+\-]?)\s*(\d{1,4}[.,]\d{2,3})(?![\d.,]*\d)")
_PAREN = re.compile(r"\(([^()]{0,40})\)")
_LEFT_OK = re.compile(r"^[\s=:/;.,\-]*(?:M[\s=:/;.,]*)?$")


def _normalise(text: str) -> str:
    s = B.fold_ascii(text or "").upper()
    s = s.replace("%%P", "±").replace("+/-", "±").replace("+-", "±").replace("-+", "±")
    s = s.replace("−", "-").replace("–", "-")             # minus sign, en dash
    return re.sub(r"\s+", " ", s).strip()


def _kind_of(text: str) -> tuple[Optional[str], bool, str]:
    """``(kind, keyword found, the text without the keywords)``."""
    kind, found = None, False
    for k, rx in KIND_KEYWORDS:
        if rx.search(text):
            found = True
            if kind is None and k is not None:
                kind = k
            text = rx.sub(" ", text)
    return kind, found, text


def read_mark(text: str, bare: bool = False) -> Optional[dict]:
    """``parse_mark`` plus ``note`` and ``bare``; ``bare=True`` also takes a value with neither sign nor keyword
    (the caller saw a mark attribute tag or a mark symbol next to it)."""
    raw = text if isinstance(text, str) else ""
    s = _normalise(raw)
    if not s or len(s) > 80:
        return None
    notes = _PAREN.findall(s)
    body = _PAREN.sub(" ", s)
    nums = list(_NUM.finditer(body))
    if not nums or len(nums) > 2:
        return None
    rest = _NUM.sub(" ", body)
    kind, keyword, rest = _kind_of(rest)
    note_kind = None
    for n in notes:                                  # ``(şev üst kotu)`` names the kind; ``(dük)`` is a free note
        k, found, _ = _kind_of(n)
        keyword = keyword or found
        note_kind = note_kind or k
    kind = kind or note_kind
    if not _LEFT_OK.match(rest):
        return None                                  # another word, a unit (M2), a dimension chain
    signs = [m.group(1) for m in nums]
    values = [float(m.group(2).replace(",", ".")) for m in nums]
    signed = any(signs)
    if not (signed or keyword or bare):
        return None
    if any("." in m.group(2) and "," in m.group(2) for m in nums):
        return None

    def rel(i: int) -> bool:
        return bool(signs[i]) or values[i] == 0.0 or values[i] < ABSOLUTE_FROM_M

    def val(i: int) -> float:
        return -values[i] if signs[i] == "-" else values[i]

    if len(nums) == 2:
        r = [i for i in (0, 1) if rel(i)]
        a = [i for i in (0, 1) if not rel(i)]
        if len(r) != 1 or len(a) != 1:
            return None
        value, relative, absolute = val(r[0]), True, values[a[0]]
        if kind is None and "=" in body:
            kind = "datum"
    else:
        relative = rel(0)
        value = val(0)
        absolute = None if relative else value
    note = bool(re.search(r"\bKOTU\s*:", body))
    return {"value": round(value, 4) + 0.0, "relative": relative,
            "absolute": None if absolute is None else round(absolute, 4) + 0.0, "kind_hint": kind, "raw": raw,
            "note": note, "bare": not (signed or keyword)}


def parse_mark(text: str) -> Optional[dict]:
    """One text or attribute value -> the mark record, or None (module docstring; contract §13.2)."""
    rec = read_mark(text)
    if rec is None:
        return None
    return {k: rec[k] for k in ("value", "relative", "absolute", "kind_hint", "raw")}


def tag_kind(tag: Optional[str]) -> Optional[str]:
    """The kind an attribute tag names (``KOT-ARAZI`` -> ``ground_natural``), else None."""
    return TAG_KIND.get(str(tag or "").strip().upper())


def is_mark_tag(tag: Optional[str]) -> bool:
    return str(tag or "").strip().upper() in MARK_ATTRIBUTE_TAGS
