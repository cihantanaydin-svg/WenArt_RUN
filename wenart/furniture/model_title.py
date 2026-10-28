"""What a library model's own names and its audit say against it: its type, a set, the size it states, the audit's
own doubts (28 Oct 2026).

Why (the user on real04 run 20261028-005318-full): "what is this miniature table makes no sense" (cam_r_L-1_salon_3:
the drawn coffee table f_L-1_087, 0.71 x 0.41 m, got 3dwh_f2d78684d4e41a5b93b167d0 "Facit High Table W2400 D800 mm
NamNam Barstool Low back Metal Leg": a 2.4 m high table with its barstools in one mesh, whose GLB box 2.4 x 1.39 x
1.08 the 3D Warehouse fix-up read in feet because only that unit put it inside a coffee table's sizes; 2400 / 732 =
3.28 = 1 / 0.3048) and "This makes no sense and terrible sink" (cam_r_L0_e_banyo_1, again in cam_r_L-1_banyo_1: the
washbasins f_L0_006 and f_L-1_026 got 3dwh_9314d5619fde2de825a4a2a1 "Sink" from the zip's Kitchen folder, a double
bowl kitchen sink with a drainboard hung on the wall; five real04 bathrooms carried it). The audit had kept both: its
title check reads "table" as naming a coffee table and "sink" as naming a washbasin, the old title size check read
only "a x b x c cm" listings and warned, and the vision doubts ("more than one object", "a table_dining") keep a model
by decision 1a. Every rule here is general: the two models are the test cases.

What (pure; ``findings(entry)`` -> ``[{"rule", "status": "refuse" | "fix" | "review", "reason", "metrics",
"fix"?}]``, ``refusal(entry)`` the joined reasons, None when nothing speaks against the model):

- ``stated_size`` (``stated_sizes``, ``size_finding``): a title that states two or more sides of its size ("W2400 D800
  mm", "120 x 60 x 36cm", 34"h x 30"w, "3' 9" x 5' 9"") is compared with the model's box (the catalogue box, or a
  fitted asset's box divided by its fit scale) over the assignments its labels allow (H on the height, W / D / L / B /
  T / diameter on a footprint side, an unlabelled side anywhere). It agrees (``agrees``) when no box side falls short
  of its stated side by more than ``SIZE_TOL`` and no footprint side exceeds it by more than ``EXCESS_TOL`` (a chaise,
  a set's stools, an open door make the box larger; a height may be exceeded at will: a headboard, a tap, a lamp's
  shade, a shower's screen over its tray). Otherwise the unit ratios (``CORRECTIONS``: feet 0.3048, inch 0.0254, cm,
  mm, x10, x100 ... read as metres or as each other) are tried on the box: one that brings every stated side within
  ``SIZE_TOL`` and leaves a box of the model's real type (``sizes`` ranges) is a ``fix`` (``rescale``); one whose box
  fits no real piece of the type, or that brings only the largest stated side within ``UNIT_TIGHT`` (the Facit
  table: in metres its width is the stated 2.4 m, its depth holds the stools), is a refusal naming the unit; no unit
  explains it: a refusal (stated and measured disagree) for furniture and decor of a size of its own (not
  ``FREE_SIZE_TYPES``, which the fit sizes to the room or wall). A single stated number ("14 Inch Height", "60W",
  "Model 2400") is never read (which side it names is a guess), nor a range or an alternative ("39-57"L", "160/205
  x 90"), nor a side outside ``SANE_M``. A group without a unit ("80x36", "30x60", "160x200") only confirms: it agrees
  when one of mm, cm or inches makes it agree, it never refuses (the unit would be a guess).
- ``title_set`` (``set_finding``): a furniture model whose names name two pieces of a group (``SET_PAIRS``: a table
  or desk with chairs, stools, barstools or a bench; a sofa with an armchair, an ottoman or a coffee table; an
  armchair or chair with an ottoman; a bed with nightstands; a toilet with a basin, a bath or a shower) joined
  (``JOIN_WORDS``: and, with, &, +, inkl., ve, und, avec, con ...), counted or plural ("6 chairs", "Sky Chairs"), with
  a stated size between them (two product names: "High Table W2400 D800 mm NamNam Barstool"), or with the vision
  check's "more than one object" is a set: never one piece of any type. A mixed set named as such
  (``MIXED_SET_WORDS``: "dining set", "bistro set", "bedroom set" ...) too. A modifier is no member ("Office Desk
  Guest Chair": no join, no count), nor a piece named for another ("bar stool for kitchen table": ``CONTEXT_WORDS``).
  A pack of one type (``PACK_WORDS``: "set of 2", "pair", "sofa set", "3-piece") is refused only when the vision check
  also saw more than one object (an ABO listing of two chairs has one chair's mesh, a 3-piece sectional is one sofa).
- ``title_type`` (``type_finding``): the title names another type than the catalogue type (``keywords.title_check``
  verdict ``conflict``; its suggested type in the reason). Sinks and basins (``SINK_TYPES``) by their use: a
  washbasin needs bathroom evidence (``BATHROOM_WORDS``: basin, washbasin, lavatory, vanity, bathroom sink, lavabo,
  Waschbecken, wastafel ...; the source's own record: the 3D Warehouse folder "Bathroom", HSSD ``found_in:
  bathroom``; our generated titles name the type they were made for; or ``audit.title_review``); a title that names a
  sink and nothing else ("Sink", "glass sink") or a kitchen word (``KITCHEN_WORDS``: kitchen, drainer, drainboard,
  double bowl, inset, commercial, the source folder "Kitchen") is no washbasin; a title that names no type at all
  rests on the audit's two vision passes (the audit's rule), refused when the audit doubts the type. A
  kitchen sink whose names say bathroom and no kitchen is no kitchen sink. A title word of another type that the
  vision check names too (``vision_agrees_other``: "INODORO EXCUSADO TOILET LAVABO" as a washbasin, the vision check:
  "a toilet") refuses the model: two sources on one other type.

- ``audit_doubt`` (``doubt_finding``; the user's third case of the same run: "is this a window? how is this making
  sense?", a "WARDROBE" whose end shows a white two-pane glazed frame; vision answer is_type false, size_plausible
  false; audited ``fix``): a model the vision audit said is not its type or found the size odd of is never used as
  its catalogue type until a later audit pass confirms the type (``review``). ``front_side`` (``front_finding``): a
  model of a type whose front is its long face whose geometric front (the detail side) is 90 degrees from the front
  the audit turned it to gets a second look (``review``). ``audit_quality`` (``quality_finding``; the user's fourth
  case: a 0.37 m high "Bathtub" the vision audit rated 2 and found no real product, audited ``keep``): a furniture
  model rated ``LOW_QUALITY_MAX`` or lower, or no real product by the vision answer, is not used (``refuse``).

The extras of the catalogue (trees, doors, windows, objects: typed by their names, ``wenart.assets.warehouse``) get
the unit evidence of ``stated_size`` only (refused, never rescaled: no size table of ours confirms a corrected box;
this module imports no asset code but the title words, so ``catalog.usable`` keeps a small import closure). An
``audit.title_review`` record ``{"ok": true, "type": <the entry's type>, "by", "reason"}`` (a person or a reviewed
vision pass looked at the model) waives the rules for that type.

How it is used: ``wenart.furniture.catalog.usable`` refuses a catalogue entry with a refusal (so no fit, pin, related
type or decor pick uses it before its audit is rewritten; a ``fix`` refuses too until it is applied: the units are
wrong until then); ``wenart.assets.audit.checks.model_title_check`` turns the findings into audit records;
``python -m wenart.assets audit title-rules [--write]`` re-runs them over the catalogue
(``wenart.assets.audit.write.apply_title_rules``); ``fitted_findings(building)`` checks the fitted pieces of a run
(the fit report, the code critic's library family, check ``LT``, Argus's process line, check ``P11``).
"""
from __future__ import annotations

import html
import math
import re
from functools import lru_cache
from itertools import permutations
from typing import Optional

RULE = "model_title"                 # the rule id of an exclusion (fit) and of the audit records
VERSION = "model-title-1"            # the catalogue pass's version (audit.title_rules.version)
CHECK = "LT"                         # the code critic's and the fit report's check id (library title)
SIZE_TOL = 0.25                      # a box side may fall short of its stated side by 25 % (unit errors are x2.54+)
EXCESS_TOL = 1.0                     # a footprint side may exceed its stated side up to x2 (a chaise, a set's stools)
UNIT_TIGHT = 0.03                    # the largest stated side this close at another unit: the units were read wrong
SANE_M = (0.005, 20.0)               # a stated side outside this is no furniture size (a typo: "2286x386740 mm")
SIZE_FIT_TOL = 0.15                  # = sizes.fits: the corrected box must be a real piece of the type
FREE_SIZE_TYPES = ("rug", "wall_art", "curtain", "blind", "throw")   # sized by the fit to the room or the wall
EXTRA_KINDS = ("vegetation", "opening", "object")
UNIT_FACTORS: tuple[tuple[float, str], ...] = ((1.0, "metres"), (0.0254, "inches"), (0.01, "centimetres"),
                                               (0.001, "millimetres"), (0.3048, "feet"))
# the corrections tried on a box: every ratio of two units (x 3.2808: a box in metres read as feet, back in metres;
# x 0.0254, x 100, x 10, ...), each with the units it means (read as, should be)
CORRECTIONS: tuple[tuple[float, str, str], ...] = tuple(
    (fb / fa, ua, ub) for fa, ua in UNIT_FACTORS for fb, ub in UNIT_FACTORS if ua != ub)
UNITLESS_TRIES: tuple[tuple[str, float], ...] = (("mm", 0.001), ("cm", 0.01), ("in", 0.0254))

# --------------------------------------------------------------------------
# Names
# --------------------------------------------------------------------------


def entry_type(entry: dict) -> str:
    """The type of a catalogue entry or audit item: a decor entry's ``decor_type`` (``decor_vase`` -> ``vase``)."""
    t = str(entry.get("decor_type") or entry.get("type") or "")
    return t[len("decor_"):] if t.startswith("decor_") else t


def is_decor(entry: dict) -> bool:
    return entry.get("kind") == "decor" or bool(entry.get("decor_type")) or \
        str(entry.get("type") or "").startswith("decor_")


def is_extra(entry: dict) -> bool:
    return entry.get("kind") in EXTRA_KINDS


def names_of(entry: dict) -> str:
    """The model's own names: its title and name (HTML entities read: "&amp;"), each once."""
    seen: list[str] = []
    for key in ("title", "name"):
        text = html.unescape(str(entry.get(key) or "")).strip()
        if text and text not in seen and not any(text in s for s in seen):
            seen.append(text)
    return " | ".join(seen)


_ZIP_MEMBER = re.compile(r"zip member (.+?)\)\s*$")


def source_context(entry: dict) -> str:
    """The source's own record of where the model belongs: the 3D Warehouse zip folders above the model ("Kitchen",
    "Bathroom"; not the zip's top folder, not the model's own folder; from the ``3dwh`` record, or a fitted asset's
    ``source_url``) and HSSD's ``found_in`` room."""
    if entry.get("_context") is not None:
        return str(entry["_context"])                     # the cached copy (``_findings_cached``) carries it
    words: list[str] = []
    rec = entry.get("3dwh") if isinstance(entry.get("3dwh"), dict) else {}
    rel = str(rec.get("rel") or "")
    if not rel and str(entry.get("source") or entry.get("library") or "") == "3dwh":
        m = _ZIP_MEMBER.search(str(entry.get("source_url") or ""))
        rel = m.group(1) if m else ""
    if rel:
        parts = rel.split("/")[:-1]                       # the folders
        if parts and parts[0] == "3D Warehouse Furniture":
            parts = parts[1:]
        if parts and re.search(r"\[[0-9A-Fa-f]{6,}\]\s*$", parts[-1]):
            parts = parts[:-1]                            # the model's own folder ("Sink [3dd30a43]") is its name
        words += parts
    hssd = entry.get("hssd") if isinstance(entry.get("hssd"), dict) else {}
    if hssd.get("found_in"):
        words.append(str(hssd["found_in"]))
    return " ".join(words)


def review_waiver(entry: dict) -> Optional[str]:
    """The ``audit.title_review`` that waives the rules for the entry's type (module docstring), else None."""
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    rev = audit.get("title_review") if isinstance(audit.get("title_review"), dict) else {}
    if rev.get("ok") is True and rev.get("type") in (None, entry_type(entry)):
        return f"title review by {rev.get('by') or '?'}: {rev.get('reason') or 'no reason'}"
    return None


# --------------------------------------------------------------------------
# Stated sizes
# --------------------------------------------------------------------------

_TOKEN = re.compile(r"\d+(?:[.,]\d+)?|[^\W\d_]+|[\"”″“]|''|['’′]|[×*/,:;=+&()\-–~]|\S", re.UNICODE)
LABELS = {"w": "w", "width": "w", "wide": "w", "b": "w", "breite": "w", "l": "l", "length": "l", "long": "l",
          "lange": "l", "d": "d", "depth": "d", "deep": "d", "t": "d", "tiefe": "d", "dia": "dia", "diam": "dia",
          "diameter": "dia", "ø": "dia", "h": "h", "height": "h", "high": "h", "tall": "h", "hohe": "h", "hoehe": "h"}
FOOT_LABELS = ("w", "l", "d", "dia")
UNIT_WORDS = {"mm": ("mm", 0.001), "cm": ("cm", 0.01), "m": ("m", 1.0), "inch": ("in", 0.0254),
              "inches": ("in", 0.0254), "in": ("in", 0.0254), '"': ("in", 0.0254), "”": ("in", 0.0254),
              "″": ("in", 0.0254), "“": ("in", 0.0254), "''": ("in", 0.0254), "ft": ("ft", 0.3048),
              "feet": ("ft", 0.3048), "foot": ("ft", 0.3048), "'": ("ft", 0.3048), "’": ("ft", 0.3048),
              "′": ("ft", 0.3048)}
QUOTES = ('"', "”", "″", "“", "''", "'", "’", "′")
CROSS = ("x", "×", "*", "by")
LABEL_JOIN = (",", ";")              # "W 120, D 60, H 75 cm": labelled sides may be listed with these between
ALTERNATIVE = ("-", "–", "/", "~", "to", "or")   # "39-57"L", "160/205 x 90": a range or an alternative


def _tokens(text: str) -> list[dict]:
    out = []
    for m in _TOKEN.finditer(text):
        tok = m.group(0)
        low = tok.lower()
        # "34"hx30"w": the letters "hx" are a label and a cross
        if len(low) == 2 and low[1] == "x" and low[0] in ("w", "d", "h", "l", "b", "t"):
            out.append({"t": low[0], "raw": tok[0], "s": m.start(), "e": m.start() + 1})
            out.append({"t": "x", "raw": "x", "s": m.start() + 1, "e": m.end()})
            continue
        out.append({"t": low, "raw": tok, "s": m.start(), "e": m.end()})
    return out


def _number(tok: Optional[dict]) -> Optional[float]:
    if tok and re.fullmatch(r"\d+(?:[.,]\d+)?", tok["t"]):
        return float(tok["t"].replace(",", "."))
    return None


def _unit_at(toks: list[dict], i: int, text: str, num_tok: dict) -> Optional[tuple[str, float, int]]:
    """``(unit, metres per unit, tokens used)`` of the unit right after a number, or None. "m" only lower case (3M is a
    brand), "in" only written onto the number or with a dot ("30in", "30 in."), a quote mark only as a unit when no
    other letter follows it ("70's", "Children's") and a feet mark only on its number."""
    if i >= len(toks):
        return None
    tok = toks[i]
    raw, low = tok["raw"], tok["t"]
    if low in ("mm", "cm", "inch", "inches", "ft", "feet", "foot"):
        return UNIT_WORDS[low][0], UNIT_WORDS[low][1], 1
    if raw == "m":
        return "m", 1.0, 1
    if low == "in":
        attached = tok["s"] == num_tok["e"]
        dotted = i + 1 < len(toks) and toks[i + 1]["t"] == "."
        return ("in", 0.0254, 2 if dotted else 1) if (attached or dotted) else None
    if raw in QUOTES:
        after = text[tok["e"]:tok["e"] + 1]
        if after.isalpha() and after.lower() not in ("w", "d", "h", "l", "x"):
            return None
        if raw in ("'", "’", "′") and tok["s"] != num_tok["e"]:
            return None
        return UNIT_WORDS[raw][0], UNIT_WORDS[raw][1], 1
    return None


def _label(tok: Optional[dict]) -> Optional[str]:
    return LABELS.get(tok["t"]) if tok else None


def _read_numbers(text: str, toks: list[dict]) -> list[dict]:
    """Every number of a title with its label (before or after it), its unit and its token span; a feet value with
    its inches ("3' 9"") is one number."""
    entries: list[dict] = []
    i = 0
    while i < len(toks):
        n = _number(toks[i])
        if n is None:
            i += 1
            continue
        prev = toks[i - 1] if i > 0 else None
        glued_word = prev is not None and prev["e"] == toks[i]["s"] and prev["raw"].isalpha() and len(prev["raw"]) > 1 \
            and _label(prev) is None
        pre = _label(prev)
        if pre and i > 1 and _number(toks[i - 2]) is not None and prev["s"] == toks[i - 2]["e"]:
            pre = None                          # "60W 40": the label is written onto the number before it
        if pre and i > 1 and toks[i - 2]["raw"].isalnum() and toks[i - 2]["e"] == prev["s"]:
            pre = None                          # "B075X12": a code, no label
        num_tok = toks[i]
        j = i + 1
        unit = _unit_at(toks, j, text, num_tok)
        if unit:
            j += unit[2]
            # "3' 9"": feet with inches
            if unit[0] == "ft" and _number(toks[j] if j < len(toks) else None) is not None:
                u2 = _unit_at(toks, j + 1, text, toks[j])
                if u2 and u2[0] == "in":
                    n = n + _number(toks[j]) / 12.0           # in feet: 3' 9" = 3.75 ft
                    j += 1 + u2[2]
        post = None
        if j < len(toks) and _label(toks[j]) and not pre:
            nxt = toks[j + 1] if j + 1 < len(toks) else None
            glued = nxt is not None and nxt["s"] == toks[j]["e"] and nxt["raw"].isalpha() and nxt["t"] not in CROSS
            if _number(nxt) is None and not glued:
                post = _label(toks[j])          # '76"W', '34"h x': the label after its number
                j += 1
        code = glued_word or (j < len(toks) and toks[j]["s"] == toks[j - 1]["e"] and toks[j]["raw"].isalpha()
                              and not unit and not post and toks[j]["t"] not in CROSS)
        entries.append({"value": n, "label": pre or post, "unit": unit[:2] if unit else None, "start": i, "end": j,
                        "s": (prev["s"] if pre else num_tok["s"]), "e": toks[j - 1]["e"], "code": bool(code)})
        i = j
    return entries


def stated_sizes(title: Optional[str]) -> list[dict]:
    """The sizes a title states, in metres: ``[{"dims": [(label | None, metres)], "unit", "text", "unit_from",
    "unitless": [(unit, dims)]}]``, one record per group of two or more sides ("120 x 60 x 36cm", "W2400 D800 mm",
    34"h x 30"w). ``label``: ``w``, ``l``, ``d``, ``dia`` (a footprint side), ``h`` (the height) or None.
    ``unit_from``: ``title``, or ``none`` for a group without a unit (``dims`` empty, ``unitless`` the readings in
    mm, cm and inches: it can only confirm). Single numbers, ranges, alternatives and codes are left out."""
    text = html.unescape(str(title or ""))
    toks = _tokens(text)
    entries = _read_numbers(text, toks)
    groups: list[list[dict]] = []
    alt: set = set()
    for k, ent in enumerate(entries):
        if groups:
            last = groups[-1][-1]
            lo = last["end"]
            hi = ent["start"] - (1 if ent["label"] and ent["start"] > 0 and _label(toks[ent["start"] - 1])
                                 and ent["s"] < toks[ent["start"]]["s"] else 0)
            between = [t["t"] for t in toks[lo:hi]]
            if len(between) == 1 and between[0] in ALTERNATIVE:
                alt.add(id(last))
                alt.add(id(ent))
            crossed = len(between) == 1 and between[0] in CROSS
            labelled = bool(last["label"] and ent["label"]) and (not between or (len(between) == 1 and between[0]
                                                                                 in LABEL_JOIN))
            if crossed or labelled:
                groups[-1].append(ent)
                continue
        groups.append([ent])
    out = []
    for g in groups:
        if len(g) < 2 or any(id(e) in alt or e["code"] for e in g):
            continue
        units = [e["unit"] for e in g if e["unit"]]
        rec = {"text": text[g[0]["s"]:g[-1]["e"]].strip(), "labels": [e["label"] for e in g]}
        if units:
            tail = g[-1]["unit"] or units[-1]
            dims = [(e["label"], round(e["value"] * (e["unit"] or tail)[1], 4)) for e in g]
            if not all(SANE_M[0] <= v <= SANE_M[1] for _l, v in dims):
                continue
            rec.update(dims=dims, unit="/".join(dict.fromkeys(u[0] for u in units)), unit_from="title", unitless=[])
        else:
            tries = [(name, [(e["label"], round(e["value"] * f, 4)) for e in g]) for name, f in UNITLESS_TRIES]
            tries = [(name, dims) for name, dims in tries if all(SANE_M[0] <= v <= SANE_M[1] for _l, v in dims)]
            if not tries:
                continue
            rec.update(dims=[], unit=None, unit_from="none", unitless=tries)
        out.append(rec)
    return out


def _ratio_error(a: float, b: float) -> float:
    if a <= 0 or b <= 0:
        return math.inf
    return max(a / b, b / a) - 1.0


def _assignments(dims, box):
    """Each assignment of the stated sides to box sides the labels allow: ``[(label, stated, measured, axis)]``."""
    box = [float(v) for v in box]
    for perm in permutations(range(3), len(dims)):
        if any(label == "h" and p != 2 or label in FOOT_LABELS and p == 2 for (label, _v), p in zip(dims, perm)):
            continue
        yield [(label, v, box[p], p) for (label, v), p in zip(dims, perm)]


def side_errors(dims, box) -> Optional[list[dict]]:
    """The best assignment for ``agrees``: per side ``{"label", "stated", "box", "short", "excess"}`` (ratios - 1),
    None when no assignment exists."""
    best, best_key = None, None
    for rows in _assignments(dims, box):
        sides = [{"label": label, "stated": v, "box": b, "axis": p, "short": max(0.0, v / b - 1.0),
                  "excess": max(0.0, b / v - 1.0)} for label, v, b, p in rows]
        key = max(max(s["short"] / SIZE_TOL, (s["excess"] / EXCESS_TOL) if s["axis"] != 2 else 0.0) for s in sides)
        if best_key is None or key < best_key:
            best, best_key = sides, key
    return best


def agrees(dims, box) -> bool:
    """No box side short of its stated side by more than ``SIZE_TOL``, no footprint side over it by more than
    ``EXCESS_TOL`` (a height may be exceeded: parts on top), for the best assignment."""
    sides = side_errors(dims, box)
    return bool(sides) and all(s["short"] <= SIZE_TOL + 1e-9 and (s["axis"] == 2 or s["excess"] <= EXCESS_TOL + 1e-9)
                               for s in sides)


def stated_error(dims, box) -> float:
    """The smallest worst two-sided ratio error of the stated sides against the box over the allowed assignments (the
    test of a unit correction: every side within ``SIZE_TOL``)."""
    errs = [max(_ratio_error(b, v) for _l, v, b, _p in rows) for rows in _assignments(dims, box)]
    return min(errs) if errs else math.inf


def model_box(entry: dict) -> Optional[list[float]]:
    """The model's own box in metres (w, d, h): a catalogue entry's ``bbox_m``; a fitted asset's box divided by its
    ``fit_scale``; None without a box."""
    box = entry.get("bbox_m")
    if not (isinstance(box, (list, tuple)) and len(box) == 3):
        return None
    try:
        vals = [float(v) for v in box]
    except (TypeError, ValueError):
        return None
    fs = entry.get("fit_scale")
    if isinstance(fs, (list, tuple)) and len(fs) == 3 and "asset_id" in entry:
        try:
            vals = [v / float(s) for v, s in zip(vals, fs)]
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    return vals if all(v > 0 and math.isfinite(v) for v in vals) else None


def _type_error(ftype: str, box) -> float:
    """How far a corrected box is outside the type's real sizes (``sizes.range_error``); a type without a range (the
    extras): ``inf``, so a unit correction is never applied without a real size behind it (refused instead). No
    import of ``wenart.assets.warehouse``: this module is read by ``catalog.usable`` in every stage, and its import
    closure stays small (tests/test_run_stages.py)."""
    from wenart.furniture import sizes as SZ
    if SZ.real_range(ftype) is not None:
        return SZ.range_error(ftype, box, oriented=False)
    return math.inf


def _fmt(box) -> str:
    return " x ".join(f"{float(v):.2f}" for v in box)


def _dims_text(dims) -> str:
    return " x ".join(f"{(label or '').upper()}{v:.3g}" for label, v in dims) + " m"


def _source_factor(entry: dict) -> Optional[float]:
    rec = entry.get("3dwh") if isinstance(entry.get("3dwh"), dict) else {}
    f = rec.get("factor")
    return float(f) if isinstance(f, (int, float)) and not isinstance(f, bool) and f > 0 else None


def size_finding(entry: dict) -> Optional[dict]:
    """``stated_size`` (module docstring): None (no stated size of two or more sides, or it agrees), a ``fix`` with
    ``rescale`` (the units were read wrong and the corrected box is a real piece of the type), or a ``refuse``."""
    if entry.get("source") == "generated" or entry_type(entry) in FREE_SIZE_TYPES:
        return None
    box = model_box(entry)
    groups = stated_sizes(names_of(entry))
    if box is None or not groups:
        return None
    for g in groups:
        if g["dims"] and agrees(g["dims"], box) or any(agrees(d, box) for _u, d in g["unitless"]):
            return None                                   # one stated size agrees: the names agree with the box
    groups = [g for g in groups if g["dims"]]
    if not groups:
        return None                                       # only unitless sizes: they never refuse
    ftype = entry_type(entry)
    undo = _source_factor(entry)
    best_fix, best_hint = None, None
    for g in groups:
        largest = max(v for _l, v in g["dims"])
        for c, read_as, should in CORRECTIONS:
            fixed = [v * c for v in box]
            prefer = 0 if undo and abs(c * undo - 1.0) < 1e-6 else 1      # the source's own unit factor undone
            e2 = stated_error(g["dims"], fixed)
            if e2 <= SIZE_TOL:
                cand = (prefer, e2, c, read_as, should, g, fixed)
                if best_fix is None or cand[:2] < best_fix[:2]:
                    best_fix = cand
                continue
            sides = side_errors(g["dims"], fixed) or []
            main = [s for s in sides if abs(s["stated"] - largest) < 1e-9]
            if main and _ratio_error(main[0]["box"], main[0]["stated"]) <= UNIT_TIGHT:
                cand = (prefer, _ratio_error(main[0]["box"], main[0]["stated"]), c, read_as, should, g, fixed)
                if best_hint is None or cand[:2] < best_hint[:2]:
                    best_hint = cand
    g0 = groups[0]
    metrics = {"stated": [[label, v] for label, v in g0["dims"]], "stated_text": g0["text"], "unit": g0["unit"],
               "box_m": [round(v, 4) for v in box], "error": round(stated_error(g0["dims"], box), 3)}
    for cand, status in ((best_fix, "fix"), (best_hint, "hint")):
        if cand is None:
            continue
        _p, _e, c, read_as, should, g, fixed = cand
        metrics.update(stated=[[label, v] for label, v in g["dims"]], stated_text=g["text"], unit=g["unit"],
                       factor=round(c, 6), read_as=read_as, should_be=should,
                       corrected_box_m=[round(v, 4) for v in fixed])
        why = (f"the title states {g['text']} ({_dims_text(g['dims'])}); the box {_fmt(box)} m was read in "
               f"{read_as}: in {should} it is {_fmt(fixed)} m")
        if status == "fix" and _type_error(ftype, fixed) <= SIZE_FIT_TOL + 1e-9:
            return {"rule": "stated_size", "status": "fix", "reason": f"{why} (units corrected x{c:.4f})",
                    "fix": {"rescale": round(c, 6)}, "metrics": metrics}
        if status == "fix":
            return {"rule": "stated_size", "status": "refuse", "metrics": metrics,
                    "reason": f"{why}: no real {ftype} at that size (its units were read so that it fits a {ftype})"}
        return {"rule": "stated_size", "status": "refuse", "metrics": metrics,
                "reason": (f"{why}, its largest stated side, and the other sides still disagree: refused until its "
                           f"units and size are corrected")}
    if is_extra(entry):
        return None                                       # the extras: unit evidence only
    s0 = side_errors(g0["dims"], box) or []
    worst = max(s0, key=lambda s: max(s["short"], s["excess"] if s["axis"] != 2 else 0.0)) if s0 else None
    how = (f"{worst['box']:.2f} m measured for a stated {worst['stated']:.3g} m" if worst else "no side matches")
    return {"rule": "stated_size", "status": "refuse", "metrics": metrics,
            "reason": (f"the title states {g0['text']} ({_dims_text(g0['dims'])}), the box is {_fmt(box)} m ({how}; "
                       f"no unit explains it): stated and measured sizes disagree")}


# --------------------------------------------------------------------------
# Sets
# --------------------------------------------------------------------------

SEAT_FAMILIES = ("chair", "armchair", "office_chair", "stool", "bar_stool", "bench")
TABLE_FAMILIES = ("table", "table_dining", "table_coffee", "desk", "side_table", "console_table")
# (anchor families, member families): the pieces of one group a single mesh may hold
SET_PAIRS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (TABLE_FAMILIES, SEAT_FAMILIES),
    (("sofa", "sofa_corner"), ("armchair", "ottoman", "table_coffee", "side_table")),
    (("armchair", "chair"), ("ottoman",)),
    (("bed", "bed_single", "bed_double"), ("nightstand",)),
    (("toilet",), ("washbasin", "sink", "bathtub", "shower")),
    (("bathtub", "shower"), ("washbasin", "sink")),
)
JOIN_WORDS = ("and", "with", "plus", "inkl", "incl", "including", "includes", "ve", "ile", "und", "mit", "et",
              "avec", "y", "con", "e", "en", "met", "och", "og")
# a piece named after these describes what another piece is for ("bar stool for kitchen table")
CONTEXT_WORDS = ("for", "to", "fits", "fit", "matching", "match", "per", "pour", "para", "fur", "icin", "zu")
# mixed sets named as such (folded phrases; keywords syntax: "~stem" inside a token)
MIXED_SET_WORDS: tuple[str, ...] = (
    "dining set", "dinette set", "dinette", "table and chairs", "table and chair", "chairs and table", "bistro set",
    "bar set", "pub set", "patio set", "garden set", "bedroom set", "bedroom suite", "living room set", "lounge set",
    "room set", "furniture set", "furniture pack", "props pack", "yemek takimi", "masa sandalye takimi",
    "yatak odasi takimi", "~essgruppe", "~sitzgruppe", "~sitzgarnitur", "eethoek", "juego de comedor",
    "set da pranzo", "ensemble salle a manger")
PACK_WORDS: tuple[str, ...] = ("set", "sets", "set of", "pair", "pair of", "pack", "piece", "pieces", "pc", "pcs",
                               "takim", "takimi", "juego", "conjunto", "lot de", "satz")
MORE_THAN_ONE = "more than one object"      # the audit's vision doubt (wenart/assets/audit/decide.py)


def _prep(text: str) -> str:
    return re.sub(r"[&+]", " and ", text)


def _family_spans(text: str) -> tuple[list[str], list[dict]]:
    """The folded tokens of ``text`` and its piece families with their token spans ``{"family", "word", "s", "e"}``."""
    from wenart.assets.audit import keywords as K
    toks, folded = K.tokens(text), K.fold(text)
    cands = []
    for fam, words in K.KEYWORDS.items():
        for w in words:
            for s, e, n in K._matches(toks, folded, w):
                cands.append((s, e, n, fam, w))
    return toks, [{"family": c[3], "word": c[4], "s": c[0], "e": c[1]} for c in K._resolve(cands) if c[0] >= 0]


def _phrase_in(toks: list[str], folded: str, words) -> list[str]:
    from wenart.assets.audit import keywords as K
    return [w for w in words if K._matches(toks, folded, w)]


def _counted(toks: list[str], span: dict) -> bool:
    """A family named in the plural ("chairs", "Stools") or after a count ("6 chairs", "2x chair")."""
    from wenart.assets.audit import keywords as K
    last = toks[span["e"] - 1] if 0 < span["e"] <= len(toks) else ""
    word_last = (K.fold(span["word"].lstrip("~")).split() or [""])[-1]
    plural = last != word_last and last in (word_last + "s", word_last + "es")
    before = toks[span["s"] - 1] if span["s"] > 0 else ""
    return plural or before.isdigit() or before in ("two", "four", "six", "eight", "pair")


def set_finding(entry: dict) -> Optional[dict]:
    """``title_set`` (module docstring) for a furniture entry: a ``refuse`` or None."""
    from wenart.assets.audit import keywords as K
    if entry.get("source") == "generated" or is_decor(entry) or is_extra(entry):
        return None
    text = _prep(names_of(entry))
    toks, spans = _family_spans(text)
    folded = K.fold(text)
    ftype = entry_type(entry)
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    seen_more = any(MORE_THAN_ONE in str(d) for d in audit.get("vision_doubt") or [])
    mixed = _phrase_in(toks, folded, MIXED_SET_WORDS)
    if mixed:
        return {"rule": "title_set", "status": "refuse",
                "reason": f"the title names a set ({', '.join(mixed)}): never one {ftype}",
                "metrics": {"words": mixed}}
    for anchors, members in SET_PAIRS:
        a = [s for s in spans if s["family"] in anchors]
        m = [s for s in spans if s["family"] in members and s["family"] not in anchors]
        for sa in a:
            for sm in m:
                first, second = (sa, sm) if sa["s"] < sm["s"] else (sm, sa)
                gap = toks[first["e"]:second["s"]]
                if any(t in CONTEXT_WORDS for t in gap):
                    continue                              # "bar stool for kitchen table": what it is for
                joined = any(t in JOIN_WORDS for t in gap)
                sized = any(t.isdigit() for t in gap)     # a stated size between two product names
                counted = _counted(toks, sm) or _counted(toks, sa)
                if not (joined or sized or counted or seen_more):
                    continue                              # a modifier: "Office Desk Guest Chair", "WC basin"
                why = ("joined" if joined else "counted" if counted else "a size between them" if sized
                       else "the vision check sees more than one object")
                return {"rule": "title_set", "status": "refuse",
                        "reason": (f"the title names a {sa['word']} and a {sm['word']} ({why}): a set of pieces in one "
                                   f"mesh, never one {ftype}"),
                        "metrics": {"anchor": sa["word"], "member": sm["word"], "evidence": why}}
    pack = _phrase_in(toks, folded, PACK_WORDS)
    if pack and seen_more:
        return {"rule": "title_set", "status": "refuse",
                "reason": (f"the title names a set ({', '.join(pack)}) and the vision check sees more than one object: "
                           f"a pack of pieces, never one {ftype}"), "metrics": {"words": pack}}
    return None


# --------------------------------------------------------------------------
# Types
# --------------------------------------------------------------------------

SINK_TYPES = ("washbasin", "sink_kitchen")
BATHROOM_WORDS: tuple[str, ...] = (
    "washbasin", "wash basin", "basin", "lavatory", "lav", "vanity", "vanity unit", "bathroom", "bath", "bathroom sink",
    "cloakroom", "cloackroom", "powder room", "wc", "lavabo", "lavamanos", "lavamano", "lave main", "~waschbecken",
    "~waschtisch", "~wastafel", "~handwaschbecken", "fontein", "handfat", "banyo", "~badezimmer", "salle de bain",
    "bagno", "bano", "vessel sink", "pedestal", "countertop basin", "counter top basin", "semi pedestal",
    "washstand", "wash stand")
KITCHEN_WORDS: tuple[str, ...] = (
    "kitchen", "kitchen sink", "drainer", "drainboard", "drain board", "draining board", "double bowl", "two bowl",
    "1 5 bowl", "bowl and a half", "one and a half bowl", "inset sink", "undermount sink", "farmhouse sink", "belfast",
    "butler sink", "utility", "laundry", "bar sink", "commercial", "sinkware", "catering", "~spule", "~spuele",
    "einbauspule", "~kuche", "~kueche", "evier", "evye", "eviye", "mutfak", "fregadero", "cocina", "lavello",
    "cucina", "~gootsteen", "~spoelbak", "keuken", "diskho", "cuisine")
SINK_WORDS: tuple[str, ...] = ("sink", "sinks")


def _sink_evidence(entry: dict) -> dict:
    """``{"bathroom": [words], "kitchen": [words], "sink": [words]}`` in the model's names and its source's record
    (``source_context``: a folder word counts like a title word, marked "(source folder)")."""
    from wenart.assets.audit import keywords as K
    names = _prep(names_of(entry))
    ctx = source_context(entry)
    out: dict = {}
    for key, words in (("bathroom", BATHROOM_WORDS), ("kitchen", KITCHEN_WORDS), ("sink", SINK_WORDS)):
        found = []
        for text, where in ((names, ""), (ctx, " (source folder)")):
            if not text:
                continue
            toks, folded = K.tokens(text), K.fold(text)
            hits = [w for w in words if K._matches(toks, folded, w)]
            # the longest phrase only ("kitchen sink" holds "kitchen")
            hits = [w for w in hits if not any(w != o and w.lstrip("~") in o for o in hits)]
            found += [w.lstrip("~") + where for w in hits]
        out[key] = list(dict.fromkeys(found))
    return out


def type_doubt(entry: dict) -> Optional[str]:
    """The audit's vision doubt about the entry's type ("the vision check says it is not a ...", "the two vision
    passes disagree ..."), None when the audit kept the type without one."""
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    for d in audit.get("vision_doubt") or []:
        if "says it is not a" in str(d) or "passes disagree" in str(d):
            return str(d)
    return None


_VISION_OTHER = re.compile(r"the vision check says it is not an? [\w ]+? \(an? ([a-z_]+)\)")


def vision_agrees_other(entry: dict, ftype: str) -> Optional[dict]:
    """The other type the title and the vision check both name (``{"type", "word"}``), else None: the audit's doubt
    "the vision check says it is not a washbasin (a toilet)" and a title word whose family names that type and not
    the entry's type ("INODORO ... TOILET LAVABO": toilet). Two sources on one other type are evidence; either alone
    is not (decision 1a keeps a vision doubt, a title word of a family holding both types names neither)."""
    from wenart.assets.audit import keywords as K
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    guesses = [m.group(1) for d in audit.get("vision_doubt") or [] for m in [_VISION_OTHER.search(str(d))] if m]
    guesses = [g for g in guesses if g != ftype and not K.near(g, ftype)]
    if not guesses:
        return None
    for f in K.named_families(names_of(entry)):
        types = K.FAMILY_TYPES.get(f["family"], ())
        if ftype in types:
            continue
        hit = next((g for g in guesses if g in types), None)
        if hit:
            return {"type": hit, "word": f["word"]}
    return None


def type_finding(entry: dict) -> Optional[dict]:
    """``title_type`` (module docstring): a ``refuse`` or None."""
    from wenart.assets.audit import keywords as K
    ftype = entry_type(entry)
    if is_extra(entry) or entry.get("source") == "generated":
        return None          # the extras are typed by their names (warehouse.name_type); generated: our own title
    other = vision_agrees_other(entry, ftype)
    if other:
        return {"rule": "title_type", "status": "refuse", "metrics": other,
                "reason": (f"the title names {other['word']} and the vision check sees a {other['type']}: a "
                           f"{other['type']}, not a {ftype}")}
    if ftype in SINK_TYPES:
        ev = _sink_evidence(entry)
        if ftype == "washbasin":
            if ev["kitchen"]:
                why = f"names {', '.join(ev['kitchen'])}: a kitchen sink, not a washbasin"
            elif ev["sink"] and not ev["bathroom"]:
                why = "names a sink and no basin, vanity or bathroom: a bare sink is a kitchen sink, not a washbasin"
            elif not ev["bathroom"] and type_doubt(entry):
                why = (f"names no basin, vanity or bathroom and {type_doubt(entry)}: no evidence it is a washbasin")
            else:
                why = None                    # a title that names no type: the audit's two vision passes typed it
        else:
            why = (f"names {', '.join(ev['bathroom'])} and no kitchen: a bathroom basin, not a kitchen sink"
                   if ev["bathroom"] and not ev["kitchen"] else None)
        if why:
            return {"rule": "title_type", "status": "refuse", "reason": f"the title {why}",
                    "metrics": {k: v for k, v in ev.items() if v}}
        return None
    chk = K.title_check(names_of(entry), ftype, str(entry.get("source") or ""))
    if chk["verdict"] != "conflict":
        return None
    from wenart.furniture import sizes as SZ
    known = set(SZ.types()) | set(SZ.decor_types())
    sug = K.suggested_type(chk, "decor" if is_decor(entry) else "furniture", known)
    words = ", ".join(chk["words"]) or "?"
    return {"rule": "title_type", "status": "refuse",
            "reason": (f"the title names {words}" + (f" (a {sug})" if sug else "") + f", not a {ftype}"),
            "metrics": {"words": chk["words"], "suggested_type": sug, "keyword_conflict": True}}


# --------------------------------------------------------------------------
# The audit's own doubts (28 Oct 2026, the user's third case of real04 run 005318)
# --------------------------------------------------------------------------

TYPE_DOUBT = "the vision check says it is not a"            # decide.py's doubt text (is_type false)
SIZE_DOUBT = "the vision check finds the size odd"          # decide.py's note (size_plausible false, code size ok)
# the types whose front is their long face (doors, drawers, seats along the width)
LONG_FRONT_TYPES = ("wardrobe", "sideboard", "dresser", "tv_unit", "bookshelf", "display_cabinet", "shoe_cabinet",
                    "tall_cabinet", "console_table", "desk", "sofa", "bench")
_TURNED = re.compile(r"front turned (90|270) deg")
# = wenart.assets.audit.checks._GEO_FRONT / _GEO_BACK (kept here so this module imports no audit code; a test pins
# the two readings equal on every catalogue note)
_GEO_FRONT = re.compile(r"geometry: [^;]*?front ([+-][XY])")
_GEO_BACK = re.compile(r"back_taller: the top \d+ % of the vertices sit toward ([+-][XY])")


def geometric_front(note: str) -> Optional[str]:
    """The front the M8-M10 geometric rule found in a ``front_axis_note`` (the detail side, or the opposite of the
    taller back), None when the note says nothing (``checks.geometric_front``)."""
    m = _GEO_FRONT.search(str(note or ""))
    if m:
        return m.group(1)
    m = _GEO_BACK.search(str(note or ""))
    if m:
        back = m.group(1)
        return ("+" if back[0] == "-" else "-") + back[1]
    return None


def doubt_finding(entry: dict) -> Optional[dict]:
    """``audit_doubt`` (the user's third case: "is this a window? how is this making sense?", the drawn wardrobe
    f_L0_023 built with 3dwh_e41345920f4dce2514160e34 "WARDROBE", whose end shows a white glazed frame; its vision
    answer: is_type false, type_guess other, size_plausible false; audited ``fix``): a model the vision audit said is
    not its type (``TYPE_DOUBT`` in ``audit.vision_doubt``) or found the size odd of (``SIZE_DOUBT`` in
    ``audit.notes``) is never used as its catalogue type until a later audit pass confirms the type (decide.py writes
    the doubt only while no second pass confirmed it): a ``review`` (the catalogue pass: ``pending``). Decision 1a of
    11 Oct 2026 kept such models with a doubt; the user's look at the renders showed the doubts were right. The
    extras (trees, doors, windows, objects) are left to their own stages."""
    if is_extra(entry):
        return None
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    texts = [str(d) for d in audit.get("vision_doubt") or [] if TYPE_DOUBT in str(d)]
    texts += [str(n) for n in audit.get("notes") or [] if SIZE_DOUBT in str(n)]
    if not texts:
        return None
    ftype = entry_type(entry)
    return {"rule": "audit_doubt", "status": "review", "metrics": {"doubts": texts},
            "reason": (f"{'; '.join(texts)}: never used as a {ftype} until a later audit pass confirms the type")}


LOW_QUALITY_MAX = 2                 # = audit.yaml quality.remove_max: a vision quality this low is no real-looking model
_VISION_QUALITY = re.compile(r"vision quality (\d)")
REAL_BY_SOURCE = ("generated", "abo", "gso")   # real_product of these comes from the source, not from the vision answer


def audit_quality(audit) -> Optional[float]:
    """The audit's vision quality (1-5): ``audit.vision_quality``, ``audit.vision.quality``, else the quality its doubt
    text names ("vision quality 2 (<= 2)"); None when the audit gives none (= ``fit.vision_quality_of``)."""
    audit = audit if isinstance(audit, dict) else {}
    q = audit.get("vision_quality")
    if q is None and isinstance(audit.get("vision"), dict):
        q = audit["vision"].get("quality")
    if q is None:
        for d in audit.get("vision_doubt") or []:
            m = _VISION_QUALITY.search(str(d))
            if m:
                return float(m.group(1))
    return float(q) if isinstance(q, (int, float)) and not isinstance(q, bool) and math.isfinite(q) else None


def quality_finding(entry: dict) -> Optional[dict]:
    """``audit_quality`` (the user's fourth case: "What kind of a bath is this" / "this bath needs to make sense", both
    real06 baths built with 3dwh_1fab322fe57d8d05759235ad "Bathtub", 0.37 m high, 85 % non-manifold edges, vision
    answer real_product false, size_plausible false, quality 2, audited ``keep``): a furniture model the vision audit
    rated ``LOW_QUALITY_MAX`` or lower (``audit.vision_quality``, or its doubt "vision quality N") or found no real
    product (``real_product`` false where the vision answer sets it: not ``REAL_BY_SOURCE``) is not used: a
    ``refuse`` (drop; no later pass of ours rates a model again). Decor and the extras keep their own rules."""
    if is_decor(entry) or is_extra(entry):
        return None
    why = []
    q = audit_quality(entry.get("audit"))
    if q is not None and q <= LOW_QUALITY_MAX:
        why.append(f"vision quality {q:g} (<= {LOW_QUALITY_MAX})")
    if entry.get("real_product") is False and str(entry.get("source") or "") not in REAL_BY_SOURCE:
        why.append("the vision check finds no real product")
    if not why:
        return None
    return {"rule": "audit_quality", "status": "refuse", "metrics": {"quality": q, "real_product":
                                                                    entry.get("real_product")},
            "reason": f"{'; '.join(why)}: not a real-looking {entry_type(entry)}"}


def front_finding(entry: dict) -> Optional[dict]:
    """``front_side`` (the same case: "geometry: detail_side: 2722 vs 108 vertices in the x slabs: front +X; M12
    audit: front turned 90 deg to +Y": the detail sat on the 0.64 m end, the window frame): a model of a type whose
    front is its long face (``LONG_FRONT_TYPES``) whose geometric front (the detail side or the taller back of
    ``front_axis_note``, ``checks.geometric_front``) is 90 degrees from the front the audit turned it to gets a second
    look (``review``): an end face with a glazed panel or a window is no wardrobe front."""
    ftype = entry_type(entry)
    if is_extra(entry) or ftype not in LONG_FRONT_TYPES:
        return None
    note = str(entry.get("front_axis_note") or "")
    if not _TURNED.search(note):
        return None
    geo = geometric_front(note.split(";")[0])
    front = str(entry.get("front_axis") or "")
    if not geo or len(front) != 2 or geo[1] == front[1]:
        return None
    return {"rule": "front_side", "status": "review", "metrics": {"geometric_front": geo, "front_axis": front},
            "reason": (f"its geometry puts the detailed face on an end ({geo}) while the audit turned its front to the "
                       f"long face ({front}): an end with a glazed panel or a window is no {ftype} front; a second "
                       f"look must confirm the model")}


# --------------------------------------------------------------------------
# All rules
# --------------------------------------------------------------------------


def _key(entry: dict) -> tuple:
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    box = model_box(entry)
    return (str(entry.get("id") or entry.get("asset_id") or ""), names_of(entry), entry_type(entry),
            str(entry.get("source") or entry.get("library") or ""),
            "decor" if is_decor(entry) else str(entry.get("kind") or ""), source_context(entry),
            tuple(round(v, 6) for v in box) if box else None,
            tuple(str(d) for d in audit.get("vision_doubt") or []), _source_factor(entry),
            tuple(str(n) for n in audit.get("notes") or [] if SIZE_DOUBT in str(n)),
            str(entry.get("front_axis_note") or ""), str(entry.get("front_axis") or ""),
            audit_quality(audit),
            entry.get("real_product") if isinstance(entry.get("real_product"), bool) else None)


@lru_cache(maxsize=65536)
def _findings_cached(key: tuple) -> tuple:
    iid, names, ftype, source, kind, ctx, box, doubts, factor, size_notes, front_note, front, vq, real = key
    entry: dict = {"id": iid, "title": names, "type": ftype, "source": source, "kind": kind, "_context": ctx,
                   "audit": {"vision_doubt": list(doubts), "notes": list(size_notes), "vision_quality": vq},
                   "front_axis_note": front_note, "front_axis": front, "real_product": real}
    if box:
        entry["bbox_m"] = list(box)
    if factor:
        entry["3dwh"] = {"factor": factor}
    out = []
    rules = (size_finding,) if kind in EXTRA_KINDS else (size_finding, set_finding, type_finding, doubt_finding,
                                                         front_finding, quality_finding)
    for fn in rules:
        got = fn(entry)
        if got:
            out.append(got)
    return tuple(out)


def findings(entry: Optional[dict]) -> list[dict]:
    """Every finding of the rules on a catalogue entry, an audit item or a fitted asset (with ``type`` given): the
    names (``stated_size``, ``title_set``, ``title_type``: ``refuse`` or ``fix``) and the audit's own doubts
    (``audit_doubt``, ``front_side``: ``review``); [] when nothing is found or an ``audit.title_review`` waives
    them. Cached by the fields read."""
    if not isinstance(entry, dict) or not entry_type(entry) or review_waiver(entry):
        return []
    return [dict(f) for f in _findings_cached(_key(entry))]


def refusal(entry: Optional[dict]) -> Optional[str]:
    """The joined reasons of the findings (a ``fix`` refuses too while it is not applied: the units are wrong until
    the catalogue is corrected; a ``review`` until a later audit pass confirms the model), None when the model may be
    used."""
    found = findings(entry)
    if not found:
        return None
    return "; ".join(f"{f['rule']}: {f['reason']}" for f in found)


# --------------------------------------------------------------------------
# A run's fitted pieces
# --------------------------------------------------------------------------


def asset_entry(piece: dict) -> Optional[dict]:
    """The entry-like record of a piece's fitted library model (its asset's title, name, box, fit scale, audit,
    source record), typed as the model's own type (a related type's model keeps its type); None for a piece built
    from code."""
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    if asset.get("method") not in (None, "library") or not asset.get("asset_id") or \
            str(asset.get("asset_id")).startswith(("parametric:", "module:", "none:", "builtin:")):
        return None
    if not (asset.get("title") or asset.get("name")):
        return None
    out = {k: asset[k] for k in ("asset_id", "title", "name", "bbox_m", "fit_scale", "audit", "source_url", "hssd",
                                 "3dwh") if k in asset}
    out.update(id=asset["asset_id"], type=asset.get("related_type") or piece.get("type"),
               source=asset.get("source") or asset.get("library"), kind="furniture")
    return out


def fitted_findings(building: Optional[dict]) -> list[dict]:
    """One violation per fitted library model the rules refuse (check ``CHECK``, major; the code critic's format
    ``{check, severity, target, room_id, message, metrics}``): its names disagree with it or its audit doubts its type
    (a pin, an older catalogue, a stale audit: a run still built it)."""
    out = []
    for f in (building or {}).get("furniture") or []:
        if not isinstance(f, dict) or f.get("build", True) is False:
            continue
        ent = asset_entry(f)
        found = findings(ent) if ent else []
        if not found:
            continue
        rules = [x["rule"] for x in found]
        out.append({"check": CHECK, "severity": "major", "target": f.get("id"), "room_id": f.get("room_id"),
                    "message": (f"{f.get('type')} {f.get('id')} is built with {ent['id']} "
                                f"\"{names_of(ent)[:80]}\", which its names or its audit refuse: "
                                + "; ".join(x["reason"] for x in found))[:600],
                    "metrics": {"asset_id": ent["id"], "rules": rules, "type": ent["type"]}})
    return out
