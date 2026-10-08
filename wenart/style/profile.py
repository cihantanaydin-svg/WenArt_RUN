"""Brief text -> style profile (Milestone 3 section 1, Milestone 10 §4.1). Deterministic, no AI.

What: ``profile_from_brief`` turns ``brief.yaml`` (``style: "..."`` or ``styles: [...]``, optionally ``exterior:``
words) into the ``style.json`` dict the Blender side consumes: floor / walls / accent wall / ceiling / wet rooms /
trim / door / window frame / cabinets / furniture looks / decor looks / exterior looks, the lighting mood and the
audit lists (``colours``, ``matched_terms``, ``unmatched_terms``, ``warnings``). ``profiles_from_brief`` returns one
profile per entry of ``styles``. ``wenart/schema/style.schema.json`` is the schema; ``docs/examples/style_m10.example.json``
the real02 profile.

How: the text is split into phrases at commas, semicolons and line breaks outside brackets. Each phrase may hold
one or more objects (``wenart/style/objects.py``: walls, floor, sofa, cushions, pots, window frames ...): the words
before an object word (else after it) are its attributes, and the colours, modifiers and materials among them apply
to that object only ("cream pots" colours the pots, never the walls). A phrase with no object word is read as in
Milestone 3: a floor word gives the floor, a wall word the walls, a bare colour word the wall colour ("charcoal and
white": charcoal walls and one white accent wall per living room and bedroom). A phrase may be split at " in " /
" with " ("many large indoor plants in rattan and cream pots"); a part with no object word continues the object
before it. Brackets are read as extra words of the plants ("(palms, monstera, ferns)").

Slots the brief does not name come from the style family word ("Scandinavian") or from ``wenart/defaults.yaml``;
every such fill is written to ``warnings`` as ``assumed: ...`` so nothing is silent. A phrase with no known word
goes to ``unmatched_terms`` with the reason in ``warnings`` (``unmatched ...``); an unknown word inside a
matched phrase is listed in ``warnings`` and never guessed. A slug never carries a colour: a slot holds
``{material, colour}`` with the colour a phrase of ``wenart/style/colours.py`` (``warm greige``).

Milestone 7 (docs/milestone7.md §6.3): the profile also records ``family``, the style family keyword of
``vocabulary.STYLE_FAMILIES`` the text (or an agreed style photo) names, ``null`` when none matched. ``refit`` uses
it to take only library models whose ``styles`` contain the family or ``neutral``; the scene builder does not read it.

Milestone 10 keeps every old slot, its meaning and its ``material`` / ``asset`` keys (``door`` stays ``door``) and
adds fields; the old slugs and keyword tables still decide the old words ("white walls" is still ``plaster_white``).
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Optional

from wenart.style import colours as C
from wenart.style import finishes as FIN
from wenart.style import objects as O
from wenart.style import vocabulary as V

DEFAULTS_PATH = Path(__file__).resolve().parents[1] / "defaults.yaml"

# The slots of the profile, in output order (shape of docs/milestone3.md §1, Milestone 10 additions between them).
PROFILE_KEYS = ("source_text", "family", "floor", "walls", "wall_accent", "ceiling", "wet_floor", "wet_walls", "trim",
                "door", "window_frame", "cabinets", "furniture", "decor", "exterior", "exterior_fallback", "lighting",
                "colours", "matched_terms", "unmatched_terms", "warnings")

# The default style text and slot fallbacks of wenart/defaults.yaml, repeated
# here so the scene builder inside Blender (whose Python has no PyYAML) gets
# the same default profile through the vocabulary. tests/test_style.py checks
# that this copy and the YAML file agree; edit both.
BUILTIN_DEFAULTS = {
    "style": {
        "text": "Scandinavian, light oak floor, white walls, linen textiles, warm daylight",
        "fallback": {"floor": "wood_oak_light", "walls": "plaster_white", "light": "warm daylight"},
        # Milestone 10 (docs/milestone10.md §1.3, §4.8): the outside looks no word names; colour "walls" = the interior
        # wall colour of the style, "interior" = the interior slot's look seen from outside.
        "exterior_fallback": {
            "facade": {"material": "render", "colour": "walls"},
            "roof": {"material": "concrete_tiles", "colour": "anthracite"},
            "window_frame": "interior",
            "door": "interior",
            "paving": {"material": "paving", "colour": "grey"},
            "garden": {"material": "grass", "colour": None},
        },
    },
}

# Bare colour words that Milestone 3 knew as wall finishes: without modifiers they keep their slug.
LEGACY_WALL_COLOURS = {"white": "plaster_white", "cream": "plaster_cream", "charcoal": "plaster_charcoal"}
# A colour word on a floor of this slug makes the colourable variant (carpet in a vocabulary colour).
FLOOR_COLOUR_VARIANT = {"carpet": "carpet_wool"}
LOOKS_LISTED_AS_ASSUMED = ("facade", "roof", "window_frame", "door", "paving", "garden")


def load_defaults() -> dict:
    """``wenart/defaults.yaml`` as a dict (style text, default profile, brief defaults).

    Raises ImportError where PyYAML is missing (Blender's Python); callers
    that only need the default profile use ``default_profile``."""
    import yaml  # lazy: the vocabulary must stay importable without PyYAML

    return yaml.safe_load(DEFAULTS_PATH.read_text(encoding="utf-8"))


def _defaults_or_builtin() -> dict:
    try:
        return load_defaults()
    except ImportError:
        return copy.deepcopy(BUILTIN_DEFAULTS)


# --------------------------------------------------------------------------
# Materials of the vocabulary
# --------------------------------------------------------------------------

def _entry(slug: Optional[str]) -> dict:
    """The vocabulary entry of a slug (style materials first, then the furniture materials); {} when unknown."""
    if not slug:
        return {}
    return V.MATERIALS.get(slug) or V.FURNITURE_MATERIALS.get(slug) or {}


def asset_of(slug: Optional[str]) -> Optional[str]:
    """The asset id of a slug, None for procedural looks, flat metals and unknown slugs."""
    return _entry(slug).get("asset") or None


def source_of(slug: Optional[str]) -> str:
    """The asset source of a slug (``polyhaven`` / ``ambientcg``), ``procedural`` when it has no file."""
    entry = _entry(slug)
    return entry.get("source") or "procedural"


def is_colourable(slug: Optional[str]) -> bool:
    """True when the style's colour name sets the base colour of the slug: flat-albedo-mode and procedural looks
    (plaster, paint, render, tiles ...), unless the entry says ``colourable: False`` (a wood tone in flat mode)."""
    entry = _entry(slug)
    if "colourable" in entry:
        return bool(entry["colourable"])
    return entry.get("albedo_mode") == "flat"


def is_wet_safe(slug: Optional[str]) -> bool:
    """True for a floor that stays in bathrooms, WCs and kitchens (the vocabulary's hard floors and ``wet_safe``)."""
    return slug in V.WET_SAFE_FLOORS or bool(_entry(slug).get("wet_safe"))


# --------------------------------------------------------------------------
# Keyword matching (the Milestone 3 helpers, kept)
# --------------------------------------------------------------------------

def split_phrases(text: str) -> list[str]:
    """Phrases of a brief text: split at commas, semicolons and line breaks outside round and square brackets,
    stripped, empty ones dropped."""
    phrases: list[str] = []
    depth, current = 0, []
    for ch in str(text or ""):
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth = max(0, depth - 1)
        if ch in ",;\n" and depth == 0:
            phrases.append("".join(current))
            current = []
        else:
            current.append(ch)
    phrases.append("".join(current))
    return [p.strip() for p in phrases if p.strip()]


def _hits(phrase_lc: str, table: list[tuple[str, str]]) -> list[tuple[int, int, str, str]]:
    """All keyword hits in a phrase as (position, -len(keyword), keyword, slug), sorted."""
    hits = []
    for keyword, slug in table:
        for m in re.finditer(r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])", phrase_lc):
            hits.append((m.start(), -len(keyword), keyword, slug))
    hits.sort()
    return hits


def _first_hit(phrase_lc: str, table: list[tuple[str, str]], skip_keywords=()) -> tuple[Optional[str], list[str]]:
    """The winning slug of a phrase and the keywords of losing hits with another slug.

    Earliest position wins; at the same position the longest keyword wins
    ("warm daylight" beats "daylight"). Losing hits that would give a
    different slug are returned so the caller can report them.
    """
    hits = [h for h in _hits(phrase_lc, table) if h[2] not in skip_keywords]
    if not hits:
        return None, []
    pos, neg_len, _, slug = hits[0]
    end = pos - neg_len
    # Hits inside the winning keyword ("plaster" inside "cream plaster") are not separate words.
    others = sorted({kw for p, _, kw, s in hits[1:] if s != slug and not (pos <= p < end)})
    return slug, others


# --------------------------------------------------------------------------
# The phrase parser
# --------------------------------------------------------------------------

_TOKEN = re.compile(r"[^\W_][\w'’\-]*")
_BRACKETS = re.compile(r"\(([^()]*)\)|\[([^\[\]]*)\]")
_SEPARATOR = re.compile(r"\s+(?:in|with)\s+")
_WALL_FINISH_WORDS = [(kw, slug) for kw, slug in V.WALL_WORDS if slug not in LEGACY_WALL_COLOURS.values()]
_FAMILY_WORDS = [(kw, kw) for kw, _ in V.STYLE_FAMILIES]


def _normalise(phrase: str) -> str:
    """Lower case, one spelling of grey, ``&`` as ``and``, one space between words."""
    text = str(phrase or "").lower().replace("’", "'").replace("&", " and ")
    text = re.sub(r"(?<![^\W_])gray(?![^\W_])", "grey", text)
    return re.sub(r"\s+", " ", text).strip()


class Frag:
    """The attribute words of one object: ``text[start:end]`` of a lower-cased phrase, with the character ranges
    already claimed by a table word, so a word is used once (a colour word inside "light oak" is the wood, not a
    colour)."""

    def __init__(self, text: str, start: int, end: int, claimed=()):
        self.text, self.start, self.end = text, start, end
        self.sub = text[start:end]
        self.claimed: list[tuple[int, int]] = [(a - start, b - start) for a, b in claimed if a < end and b > start]

    def tokens(self) -> list[tuple[str, int, int]]:
        return [(m.group(), m.start(), m.end()) for m in _TOKEN.finditer(self.sub)]

    def free(self, tok) -> bool:
        return not any(tok[1] < b and a < tok[2] for a, b in self.claimed)

    def spans(self, table) -> list:
        return O.find_spans(self.sub, table, taken=self.claimed)

    def claim(self, span) -> None:
        self.claimed.append((span.start, span.end))

    def claim_words(self, words) -> list[str]:
        """Claim every free token that is one of ``words``; returns them."""
        found = []
        for tok in self.tokens():
            if tok[0] in words and self.free(tok):
                self.claimed.append((tok[1], tok[2]))
                found.append(tok[0])
        return found

    def colour_hits(self) -> list[dict]:
        """The colour phrases among the free tokens, in order: ``{"phrase", "start", "end", "and": bool}``
        (``and``: joined to the colour before it by "and"). Longest phrase first at each word, so ``light grey``
        is a name and ``warm greige`` a modifier plus a name."""
        toks = self.tokens()
        hits: list[dict] = []
        i = 0
        while i < len(toks):
            tok = toks[i]
            if not self.free(tok):
                i += 1
                continue
            end = None
            for j in range(min(len(toks), i + 4), i, -1):
                run = toks[i:j]
                if not all(self.free(t) for t in run):
                    continue
                if any(self.sub[run[k][2]:run[k + 1][1]].strip() for k in range(len(run) - 1)):
                    continue
                phrase = C.canonical_phrase(" ".join(t[0] for t in run))
                if phrase:
                    hits.append({"phrase": phrase, "start": run[0][1], "end": run[-1][2], "and": False})
                    end = j
                    break
            i = end if end else i + 1
        for k in range(1, len(hits)):
            between = self.sub[hits[k - 1]["end"]:hits[k]["start"]].strip()
            hits[k]["and"] = between in ("and", "+", "")
        for h in hits:
            self.claimed.append((h["start"], h["end"]))
        return hits

    def leftovers(self) -> list[str]:
        """Free tokens that are no descriptor, amount word or modifier: the unknown words."""
        return [t[0] for t in self.tokens() if self.free(t) and t[0] not in O.DESCRIPTORS
                and t[0] not in O.AMOUNT_WORDS and t[0] not in O.MODIFIER_WORDS and t[0] not in O.TEXTILE_WORDS]

    def modifiers(self) -> list[str]:
        return [t[0] for t in self.tokens() if self.free(t) and t[0] in O.MODIFIER_WORDS]


def _new_draft() -> dict:
    return {
        "floor": None, "floor_colour": None, "walls": None, "wall_colour": None, "wall_accent": None,
        "light": None, "family": None, "tags": [], "ceiling_colour": None, "trim_colour": None,
        "wet_walls": {}, "door": {}, "window_frame": {}, "cabinets": {},
        "furniture": {"wood": None, "fabric_colour": None, "by_type": {}, "accents": []},
        "decor": {"plant_species": [], "plant_amount": None, "pots": [], "cushion_colours": [], "throw_colours": [],
                  "curtain_colour": None, "rug_colours": []},
        "exterior": {}, "colours": {},
    }


class _Phrase:
    """The state of one phrase while its objects are read."""

    def __init__(self, phrase: str, draft: dict, notes: list[str], objects: set[str]):
        self.phrase, self.d, self.notes, self.objects = phrase, draft, notes, objects

    def take(self, store: dict, key: str, value, label: str) -> bool:
        """First phrase wins a single value; a later different one is noted, not applied."""
        if store.get(key) is None:
            store[key] = value
            return True
        if store[key] != value:
            self.notes.append(f"ignored {label} '{value}' from '{self.phrase}' ({label} already {store[key]})")
        return False

    def record_colours(self, obj: str, phrases: list[str]) -> None:
        if phrases:
            known = self.d["colours"].setdefault(obj, [])
            known.extend(p for p in phrases if p not in known)

    def ignore_colours(self, hits, why: str) -> None:
        if hits:
            self.notes.append(f"ignored colour '{hits[0]['phrase']}' in '{self.phrase}' ({why})")


def _apply_colour(ph: _Phrase, slug: Optional[str], colour: Optional[str], what: str) -> Optional[str]:
    """The colour to store for a slug: the colour when the slug takes one, else None with a note."""
    if not colour:
        return None
    if slug is None or is_colourable(slug):
        return colour
    ph.notes.append(f"colour '{colour}' in '{ph.phrase}' only describes {what} '{slug}' (its photo colour is kept)")
    return None


# ---- one handler per object -------------------------------------------------------------------------------------

def _h_walls(ph: _Phrase, frag: Frag, obj: str = "walls") -> int:
    fin_spans = frag.spans(_WALL_FINISH_WORDS)
    finish = fin_spans[0] if fin_spans else None
    if finish:
        frag.claim(finish)
        for other in fin_spans[1:]:
            if other.value != finish.value:
                ph.notes.append(f"ignored wall word '{other.keyword}' in '{ph.phrase}' (phrase already gives {finish.value})")
            frag.claim(other)
    plaster = None if finish else O.first_span(frag.sub, [("plaster", "plaster_white")], taken=frag.claimed)
    if plaster:
        frag.claim(plaster)
    cols = frag.colour_hits()
    main = cols[0]["phrase"] if cols else None
    accent = cols[1]["phrase"] if len(cols) > 1 and cols[1]["and"] else None
    if len(cols) > (2 if accent else 1):
        ph.notes.append(f"ignored colour '{cols[2 if accent else 1]['phrase']}' in '{ph.phrase}' (walls: a main colour and one accent colour)")
    slug = finish.value if finish else None
    if slug is None and main:
        name, mods = C.parse(main)
        if name in LEGACY_WALL_COLOURS and not mods:
            slug = LEGACY_WALL_COLOURS[name]
        else:
            slug = "plaster_white" if plaster else "paint"
    elif slug is None and plaster:
        slug = plaster.value
    if slug is None:
        return 0
    colour = _apply_colour(ph, slug, main, "the wall finish")
    if ph.take(ph.d, "walls", slug, "walls"):
        ph.d["wall_colour"] = colour
    elif colour != ph.d["wall_colour"] and colour:
        ph.notes.append(f"ignored wall colour '{colour}' from '{ph.phrase}' (walls already {ph.d['wall_colour'] or ph.d['walls']})")
    ph.record_colours(obj, [c["phrase"] for c in cols])
    if accent and ph.d["wall_accent"] is None:
        ph.d["wall_accent"] = {"material": "paint", "colour": accent}
    return 1


def _h_accent_wall(ph: _Phrase, frag: Frag) -> int:
    fin_spans = frag.spans(_WALL_FINISH_WORDS)
    finish = fin_spans[0] if fin_spans else None
    if finish:
        frag.claim(finish)
    cols = frag.colour_hits()
    if not cols and not finish:
        return 0
    slug = finish.value if finish else "paint"
    colour = _apply_colour(ph, slug, cols[0]["phrase"] if cols else None, "the accent finish")
    if ph.d["wall_accent"] is None:
        ph.d["wall_accent"] = {"material": slug, "colour": colour}
    else:
        ph.notes.append(f"ignored accent wall in '{ph.phrase}' (an accent wall is already named)")
    ph.record_colours("accent_wall", [c["phrase"] for c in cols])
    return 1


def _h_floor(ph: _Phrase, frag: Frag) -> int:
    spans = frag.spans(V.FLOOR_WORDS)
    if not spans:
        return 0
    win = spans[0]
    frag.claim(win)
    for other in spans[1:]:
        if other.value != win.value:
            ph.notes.append(f"ignored floor word '{other.keyword}' in '{ph.phrase}' (phrase already gives {win.value})")
        frag.claim(other)
    slug = win.value
    for _, (x, y) in O.tile_sizes(frag.sub):                       # "60x120 cm": the slug's own size is used
        frag.claimed.append((x, y))
    for m in re.finditer(r"grout", frag.sub):                       # "... with black grout": wet walls only
        found = Frag(frag.sub, 0, m.start(), frag.claimed).colour_hits()
        if found:
            ph.notes.append(f"ignored grout colour '{found[-1]['phrase']}' in '{ph.phrase}' (grout colour is a wet-wall slot)")
            frag.claimed.append((found[-1]["start"], found[-1]["end"]))
        frag.claimed.append((m.start(), m.end()))
    frag.claim_words({"tiles", "tile"})
    cols = frag.colour_hits()
    main = cols[0]["phrase"] if cols else None
    if main and slug in FLOOR_COLOUR_VARIANT:
        slug = FLOOR_COLOUR_VARIANT[slug]
    colour = _apply_colour(ph, slug, main, "the floor")
    if ph.take(ph.d, "floor", slug, "floor"):
        ph.d["floor_colour"] = colour
    ph.record_colours("floor", [c["phrase"] for c in cols])
    return 1


def _h_ceiling(ph: _Phrase, frag: Frag) -> int:
    cols = frag.colour_hits()
    if not cols:
        return 0
    ph.take(ph.d, "ceiling_colour", cols[0]["phrase"], "ceiling colour")
    ph.record_colours("ceiling", [c["phrase"] for c in cols])
    return 1


def _h_trim(ph: _Phrase, frag: Frag) -> int:
    cols = frag.colour_hits()
    if not cols:
        return 0
    ph.take(ph.d, "trim_colour", cols[0]["phrase"], "trim colour")
    ph.record_colours("trim", [c["phrase"] for c in cols])
    return 1


def _h_piece(ph: _Phrase, frag: Frag, obj: str) -> int:
    """A furniture type word (sofa, armchair, coffee table ...): material tags and one colour for its types."""
    tags: list[str] = []
    for span in frag.spans(O.MATERIAL_TAG_WORDS):
        frag.claim(span)
        if span.value not in tags:
            tags.append(span.value)
    cols = frag.colour_hits()
    if not cols and not tags:
        return 0
    hard = any(t in tags for t in ("wood", "metal", "glass", "rattan", "marble"))
    key = "fabric_colour" if obj in O.UPHOLSTERED and not hard else "colour"
    for t in O.OBJECT_TYPES[obj]:
        entry = ph.d["furniture"]["by_type"].setdefault(t, {"fabric_colour": None, "colour": None, "material_tags": []})
        if cols:
            if entry[key] is None:
                entry[key] = cols[0]["phrase"]
            elif entry[key] != cols[0]["phrase"]:
                ph.notes.append(f"ignored {t} colour '{cols[0]['phrase']}' in '{ph.phrase}' ({t} colour already {entry[key]})")
        for tag in tags:
            if tag not in entry["material_tags"]:
                entry["material_tags"].append(tag)
    ph.record_colours(obj, [c["phrase"] for c in cols])
    return 1


def _wood_words(frag: Frag):
    """Claim the wood type and tone words of a fragment; ``(slug, words)`` or ``(None, [])``."""
    words = [t[0] for t in frag.tokens() if frag.free(t)]
    slug = O.wood_slug(words)
    if slug is None:
        return None, []
    used = frag.claim_words(set(O.WOOD_TYPE_WORDS) | set(O.WOOD_TONE_LIGHT) | set(O.WOOD_TONE_DARK))
    return slug, used


def _h_furniture(ph: _Phrase, frag: Frag) -> int:
    slug, _ = _wood_words(frag)
    cols = frag.colour_hits()
    if slug is None:
        if cols:
            ph.notes.append(f"ignored colour '{cols[0]['phrase']}' in '{ph.phrase}' (no furniture-wide colour slot: "
                            f"name a piece, for example a sofa or a wardrobe)")
        return 0
    ph.take(ph.d["furniture"], "wood", slug, "furniture wood")
    ph.ignore_colours(cols, "furniture wood has no colour")
    return 1


def _h_decor(ph: _Phrase, frag: Frag, obj: str) -> int:
    cols = frag.colour_hits()
    if not cols:
        return 0
    names = [c["phrase"] for c in cols]
    decor = ph.d["decor"]
    if obj == "cushions":
        decor["cushion_colours"].extend(n for n in names if n not in decor["cushion_colours"])
    elif obj == "throws":
        decor["throw_colours"].extend(n for n in names if n not in decor["throw_colours"])
    elif obj == "rug":
        decor["rug_colours"].extend(n for n in names if n not in decor["rug_colours"])
    else:                                                          # curtains: one colour
        ph.take(decor, "curtain_colour", names[0], "curtain colour")
        if len(names) > 1:
            ph.notes.append(f"ignored colour '{names[1]}' in '{ph.phrase}' (curtains: one colour)")
    ph.record_colours(obj, names)
    return 1


def _h_cabinets(ph: _Phrase, frag: Frag) -> int:
    cab = ph.d["cabinets"]
    effects = 0
    front = O.first_span(frag.sub, O.CABINET_FRONT_WORDS, taken=frag.claimed)
    if front:
        frag.claim(front)
        effects += int(ph.take(cab, "front_style", front.value, "cabinet front"))
    slug, _ = _wood_words(frag)
    if slug:
        effects += int(ph.take(cab, "wood", slug, "cabinet wood"))
    cols = frag.colour_hits()
    if cols:
        effects += int(ph.take(cab, "colour", cols[0]["phrase"], "cabinet colour"))
        ph.record_colours("cabinets", [c["phrase"] for c in cols])
    return 1 if (front or slug or cols) else 0


def _h_worktop(ph: _Phrase, frag: Frag) -> int:
    span = O.first_span(frag.sub, O.WORKTOP_WORDS, taken=frag.claimed)
    if not span:
        return 0
    frag.claim(span)
    ph.take(ph.d["cabinets"], "worktop", span.value, "worktop")
    ph.ignore_colours(frag.colour_hits(), "a worktop has a material, not a colour")
    return 1


def _h_handles(ph: _Phrase, frag: Frag) -> int:
    span = O.first_span(frag.sub, O.HANDLE_WORDS, taken=frag.claimed)
    if not span:
        return 0
    frag.claim(span)
    kitchen = bool(ph.objects & {"cabinets", "kitchen", "worktop"})
    door = "doors" in ph.objects
    if door or not kitchen:
        ph.take(ph.d["door"], "handle", span.value, "door handle")
    if kitchen or not door:
        ph.take(ph.d["cabinets"], "handle", span.value, "cabinet handle")
    return 1


def _door_look(ph: _Phrase, frag: Frag) -> dict:
    """The door words of a fragment: ``{material, style, colour}`` (keys only where a word was found)."""
    out: dict = {}
    style = O.first_span(frag.sub, O.DOOR_STYLE_WORDS, taken=frag.claimed)
    if style:
        frag.claim(style)
        out["style"] = style.value
    wood = O.first_span(frag.sub, O.DOOR_WOOD_WORDS, taken=frag.claimed)
    if wood:
        frag.claim(wood)
        out["material"] = wood.value
    cols = frag.colour_hits()
    if cols:
        name, mods = C.parse(cols[0]["phrase"])
        if name == "black" and not mods:
            out.setdefault("material", "lacquer_dark")
        else:
            out.setdefault("material", "painted_wood_white")
        out["colour"] = cols[0]["phrase"] if out["material"] in ("painted_wood_white", "lacquer_dark") else None
        ph.record_colours("doors", [c["phrase"] for c in cols])
    return out


def _h_doors(ph: _Phrase, frag: Frag) -> int:
    look = _door_look(ph, frag)
    for key in ("material", "style", "colour"):
        if look.get(key):
            ph.take(ph.d["door"], key, look[key], f"door {key}")
    return 1 if look else 0


def _frame_look(ph: _Phrase, frag: Frag) -> dict:
    """The window-frame words of a fragment: ``{material, colour}`` (empty when nothing is named)."""
    word = O.first_span(frag.sub, O.FRAME_WORDS, taken=frag.claimed)
    if word:
        frag.claim(word)
    cols = frag.colour_hits()
    if not word and not cols:
        return {}
    material, colour = (word.value if word else None), (cols[0]["phrase"] if cols else None)
    if colour:
        name, mods = C.parse(colour)
        by_colour = None if mods else FIN.FRAME_COLOUR_MATERIALS.get(name)
        if material is None:
            material = by_colour or "painted_metal_white"
        elif material not in ("painted_metal_white", "oak") and by_colour != material:
            material = "painted_metal_white"                    # e.g. white aluminium: painted metal in that colour
        if material == "oak":
            ph.notes.append(f"colour '{colour}' in '{ph.phrase}' only describes the oak frame (its photo colour is kept)")
            colour = None
        elif material != "painted_metal_white" and by_colour == material:
            colour = None                                       # the material is that colour already
        ph.record_colours("window_frames", [c["phrase"] for c in cols])
    return {"material": material, "colour": colour}


def _h_window_frames(ph: _Phrase, frag: Frag) -> int:
    look = _frame_look(ph, frag)
    if not look:
        return 0
    if not ph.d["window_frame"]:
        ph.d["window_frame"] = look
    elif ph.d["window_frame"] != look:
        ph.notes.append(f"ignored window frames '{look['material']}' from '{ph.phrase}' (window frames already "
                        f"{ph.d['window_frame']['material']})")
    return 1


def _h_pots(ph: _Phrase, frag: Frag) -> int:
    """Groups split at "and": ``rattan and cream pots`` is a rattan pot and a cream pot; ``cream ceramic pots`` one."""
    toks = [t for t in frag.tokens() if frag.free(t)]
    groups: list[list] = [[]]
    for t in toks:
        if t[0] == "and":
            if groups[-1]:
                groups.append([])
        else:
            groups[-1].append(t)
    pots = []
    names: list[str] = []
    for group in groups:
        if not group:
            continue
        sub = Frag(frag.sub, group[0][1], group[-1][2])
        material = None
        mat = O.first_span(sub.sub, O.POT_MATERIAL_WORDS)
        if mat:
            sub.claim(mat)
            material = mat.value
        cols = sub.colour_hits()
        colour = cols[0]["phrase"] if cols else None
        if material or colour:
            pots.append({"material": material, "colour": colour})
            names += [c["phrase"] for c in cols]
            for t in group:
                frag.claimed.append((t[1], t[2]))
    if not pots:
        return 0
    known = ph.d["decor"]["pots"]
    known.extend(p for p in pots if p not in known)
    ph.record_colours("pots", names)
    return 1


def _h_plants(ph: _Phrase, frag: Frag, extra: str) -> int:
    text = (frag.sub + " " + extra).strip()          # the attribute words, the plant object word itself and the brackets
    species = [s.value for s in O.find_spans(text, O.PLANT_WORDS)]
    decor = ph.d["decor"]
    for sp in species:
        if sp not in decor["plant_species"]:
            decor["plant_species"].append(sp)
    amount = None
    for tok in frag.tokens():
        if tok[0] in O.AMOUNT_WORDS and frag.free(tok):
            amount = O.AMOUNT_WORDS[tok[0]]
            frag.claimed.append((tok[1], tok[2]))
            break
    if amount:
        ph.take(decor, "plant_amount", amount, "plant amount")
    for tok in frag.tokens():                                    # species words are the plants' own words
        if frag.free(tok) and any(tok[0] in kw.split() for kw, _ in O.PLANT_WORDS):
            frag.claimed.append((tok[1], tok[2]))
    return 1


def _h_exterior(ph: _Phrase, frag: Frag, slot: str, source: str = "brief") -> int:
    spans = frag.spans(O.EXTERIOR_WORDS[slot])
    if not spans:
        return 0
    frag.claim(spans[0])
    cols = frag.colour_hits()
    colour = cols[0]["phrase"] if cols else None
    slug = spans[0].value
    colour = _apply_colour(ph, slug, colour, f"the {slot}")
    if slot not in ph.d["exterior"]:
        ph.d["exterior"][slot] = {"material": slug, "colour": colour, "source": source}
    ph.record_colours(slot, [c["phrase"] for c in cols])
    return 1


def _h_wet_walls(ph: _Phrase, frag: Frag) -> int:
    spans = frag.spans(O.WET_WALL_WORDS)
    sizes = O.tile_sizes(frag.sub)
    for _, (x, y) in sizes:
        frag.claimed.append((x, y))
    grout = None
    for m in re.finditer(r"grout", frag.sub):
        before = Frag(frag.sub, 0, m.start(), frag.claimed)
        found = before.colour_hits()
        if found:
            grout = found[-1]["phrase"]
            frag.claimed.append((found[-1]["start"], found[-1]["end"]))
        frag.claimed.append((m.start(), m.end()))
    frag.claim_words({"tiles", "tile", "wall", "walls", "slab", "slabs"})
    wet = ph.d["wet_walls"]
    if not spans:
        if grout and wet and wet.get("grout_colour") is None:            # "... with dark grey grout" after the tiles
            wet["grout_colour"] = grout
            ph.record_colours("wet_walls", [grout])
            return 1
        return 0
    frag.claim(spans[0])
    cols = frag.colour_hits()
    if wet:
        ph.notes.append(f"ignored wet-wall tiles in '{ph.phrase}' (already {wet.get('material')})")
        return 1
    size = sizes[0][0] if sizes else None
    if size and (FIN.TILE_PATTERNS.get(spans[0].value) or {}).get("pattern") == "running_bond":
        size = sorted(size, reverse=True)                              # running bond: the long side is laid horizontally
    wet.update({"material": spans[0].value, "tile_size_m": size,
                "colour": cols[0]["phrase"] if cols else None, "grout_colour": grout})
    ph.record_colours("wet_walls", [c["phrase"] for c in cols] + ([grout] if grout else []))
    return 1


def _h_accents(ph: _Phrase, frag: Frag) -> int:
    cols = frag.colour_hits()
    if not cols:
        return 0
    accents = ph.d["furniture"]["accents"]
    accents.extend(c["phrase"] for c in cols if c["phrase"] not in accents)
    ph.record_colours("accents", [c["phrase"] for c in cols])
    return 1


def _h_textiles(ph: _Phrase, frag: Frag) -> int:
    cols = frag.colour_hits()
    if not cols:
        return 0
    ph.take(ph.d["furniture"], "fabric_colour", cols[0]["phrase"], "fabric colour")
    ph.record_colours("textiles", [c["phrase"] for c in cols])
    return 1


_HANDLERS = {
    "walls": lambda ph, fr, ex: _h_walls(ph, fr), "accent_wall": lambda ph, fr, ex: _h_accent_wall(ph, fr),
    "floor": lambda ph, fr, ex: _h_floor(ph, fr), "ceiling": lambda ph, fr, ex: _h_ceiling(ph, fr),
    "trim": lambda ph, fr, ex: _h_trim(ph, fr), "furniture": lambda ph, fr, ex: _h_furniture(ph, fr),
    "cushions": lambda ph, fr, ex: _h_decor(ph, fr, "cushions"), "throws": lambda ph, fr, ex: _h_decor(ph, fr, "throws"),
    "curtains": lambda ph, fr, ex: _h_decor(ph, fr, "curtains"), "rug": lambda ph, fr, ex: _h_decor(ph, fr, "rug"),
    "cabinets": lambda ph, fr, ex: _h_cabinets(ph, fr), "kitchen": lambda ph, fr, ex: _h_cabinets(ph, fr),
    "worktop": lambda ph, fr, ex: _h_worktop(ph, fr), "handles": lambda ph, fr, ex: _h_handles(ph, fr),
    "doors": lambda ph, fr, ex: _h_doors(ph, fr), "window_frames": lambda ph, fr, ex: _h_window_frames(ph, fr),
    "pots": lambda ph, fr, ex: _h_pots(ph, fr), "plants": lambda ph, fr, ex: _h_plants(ph, fr, ex),
    "wet_walls": lambda ph, fr, ex: _h_wet_walls(ph, fr), "accents": lambda ph, fr, ex: _h_accents(ph, fr),
    "textiles": lambda ph, fr, ex: _h_textiles(ph, fr), "lighting": lambda ph, fr, ex: 0,
}
for _slot_object in O.OBJECT_EXTERIOR_SLOT:
    _HANDLERS[_slot_object] = (lambda slot: lambda ph, fr, ex: _h_exterior(ph, fr, slot))(O.OBJECT_EXTERIOR_SLOT[_slot_object])
for _piece in O.OBJECT_TYPES:
    _HANDLERS[_piece] = (lambda obj: lambda ph, fr, ex: _h_piece(ph, fr, obj))(_piece)


def _bare(ph: _Phrase, core: str, claimed) -> tuple[int, list[str]]:
    """A phrase with no object word: Milestone 3's reading (a floor word, else wall words and bare colours) plus the
    style tags (``natural``); ``(effects, unknown words)``."""
    frag = Frag(core, 0, len(core), claimed)
    effects = 0
    for tag in O.find_spans(core, [(t, t) for t in O.STYLE_TAGS], taken=claimed):
        frag.claim(tag)
        if tag.value not in ph.d["tags"]:
            ph.d["tags"].append(tag.value)
        effects += 1
    if frag.spans(V.FLOOR_WORDS):
        effects += _h_floor(ph, frag)
    else:
        effects += _h_walls(ph, frag)
    return effects, frag.leftovers()


def _scan_phrase(phrase: str, d: dict, notes: list[str]) -> tuple[bool, str]:
    """Read one phrase into the draft ``d``; ``(matched, reason when not)``."""
    lc = _normalise(phrase)
    extras = [m.group(1) or m.group(2) for m in _BRACKETS.finditer(lc)]
    core = _BRACKETS.sub(" ", lc)
    claimed: list[tuple[int, int]] = []
    effects = 0

    light = O.first_span(core, V.LIGHT_WORDS)
    if light:
        claimed.append((light.start, light.end))
        effects += 1
        if d["light"] is None:
            d["light"] = light.value
        elif d["light"] != light.value:
            notes.append(f"ignored light '{light.value}' from '{phrase}' (light already {d['light']})")
    family = O.first_span(core, _FAMILY_WORDS, taken=claimed)
    if family:
        claimed.append((family.start, family.end))
        effects += 1
        if d["family"] is None:
            d["family"] = family.value
        elif d["family"] != family.value:
            notes.append(f"ignored family '{family.value}' from '{phrase}' (family already {d['family']})")

    objs = O.find_spans(core, O.OBJECT_WORDS, taken=claimed)
    unused_words: list[str] = []
    if not objs:
        ph = _Phrase(phrase, d, notes, set())
        bare_effects, unused_words = _bare(ph, core, claimed)
        effects += bare_effects
    else:
        ph = _Phrase(phrase, d, notes, {o.value for o in objs})
        extra = " ".join(extras)
        seps = [(m.start(), m.end()) for m in _SEPARATOR.finditer(core)]
        bounds = [0] + [x for sep in seps for x in sep] + [len(core)]
        previous = None
        for seg_start, seg_end in ((bounds[i], bounds[i + 1]) for i in range(0, len(bounds), 2)):
            in_seg = [o for o in objs if seg_start <= o.start < seg_end]
            if not in_seg:
                frag = Frag(core, seg_start, seg_end, claimed)
                if previous is not None:                       # "... in greige": the words belong to the object before
                    effects += _HANDLERS[previous](ph, frag, extra)
                    unused_words += _unused(frag, ph)
                else:
                    bare_effects, left = _bare(ph, frag.sub, [])
                    effects += bare_effects
                    unused_words += left
                continue
            prev_range = None
            for k, o in enumerate(in_seg):
                a, b = (in_seg[k - 1].end if k else seg_start), o.start
                limit = in_seg[k + 1].start if k + 1 < len(in_seg) else seg_end
                if o.value in O.OBJECT_IN_KEYWORDS:
                    # the object word is part of keywords ("botanical wallpaper", "wallpaper stripe", "green roof"): the
                    # words before it and after it (up to "and") are read together with it
                    tail = core[o.end:limit]
                    tail = tail[:tail.find(" and ")] if " and " in tail else tail
                    a = a if core[a:b].replace("and", " ").strip() else o.start
                    b = o.end + len(tail)
                    frag = Frag(core, a, b, claimed + [(x.start, x.end) for x in objs if x is not o])
                elif not core[a:b].replace("and", " ").strip():
                    if k and core[a:b].strip() == "and" and prev_range:      # "white walls and ceiling": share the words
                        a, b = prev_range
                    else:                                                    # nothing before the object: read behind it
                        a, b = o.end, limit
                    frag = Frag(core, a, b, claimed + [(x.start, x.end) for x in objs])
                else:
                    frag = Frag(core, a, b, claimed + [(x.start, x.end) for x in objs])
                effects += _HANDLERS[o.value](ph, frag, (extra + " " + core[o.start:o.end]) if o.value == "plants" else extra)
                if o.value in O.OBJECT_IN_KEYWORDS:
                    frag.claimed.append((o.start - a, o.end - a))                # the object word itself is known
                prev_range = (a, b)
                unused_words += _unused(frag, ph)
                previous = o.value
        if extras and not any(o.value == "plants" for o in objs):
            notes.append(f"ignored bracket text '({'; '.join(extras)})' in '{phrase}'")
    if effects == 0:
        return False, _reason(core, objs)
    if unused_words:
        notes.append(f"unknown word(s) {', '.join(repr(w) for w in dict.fromkeys(unused_words))} in '{phrase}' (not used)")
    return True, ""


def _unused(frag: Frag, ph: _Phrase) -> list[str]:
    left = frag.leftovers()
    dangling = frag.modifiers()
    if dangling:
        ph.notes.append(f"ignored modifier(s) {', '.join(repr(w) for w in dangling)} in '{ph.phrase}' (no colour word)")
    return left


def _reason(core: str, objs) -> str:
    for word, hint in O.HINTS.items():
        if re.search(r"(?<![^\W_])" + re.escape(word) + r"(?![^\W_])", core):
            return hint
    if objs:
        names = ", ".join(sorted({o.value for o in objs}))
        return f"object '{names}' found, but no known material, colour or finish word for it"
    return "no known object, material, colour, light or style word"


def match_text(text: str) -> dict:
    """Keyword scan of a brief text.

    Returns ``{"floor", "walls", "light", "family"}`` (slug or None, first
    phrase wins), ``matched`` / ``unmatched`` phrases in brief order, ``notes`` about words that were seen but
    ignored (second floor word, unknown words ...), ``reasons`` (``{unmatched phrase: why}``) and ``draft``, the
    full reading of the text (every slot of the Milestone 10 profile; see ``_new_draft``).
    """
    d = _new_draft()
    matched, unmatched, notes, reasons = [], [], [], {}
    for phrase in split_phrases(text):
        ok, why = _scan_phrase(phrase, d, notes)
        if ok:
            matched.append(phrase)
        else:
            unmatched.append(phrase)
            reasons[phrase] = why
            notes.append(f"unmatched '{phrase}': {why}")
    return {"floor": d["floor"], "walls": d["walls"], "light": d["light"], "family": d["family"],
            "matched": matched, "unmatched": unmatched, "notes": notes, "reasons": reasons, "draft": d}


# --------------------------------------------------------------------------
# Style reference photos (docs/milestone5.md §6)
# --------------------------------------------------------------------------

PHOTO_SLOTS = ("floor", "walls", "light", "family")


def photo_term_list(photo_terms) -> list[dict]:
    """The terms of a ``python -m wenart.style.photos combine`` result (a dict with ``terms``) or of a term list."""
    if not photo_terms:
        return []
    terms = photo_terms.get("terms") if isinstance(photo_terms, dict) else photo_terms
    return [t for t in (terms or []) if isinstance(t, dict)]


def _photo_value_known(slot: str, value) -> bool:
    known = {"floor": {s for _, s in V.FLOOR_WORDS}, "walls": {s for _, s in V.WALL_WORDS},
             "light": set(V.LIGHTING), "family": {name for name, _ in V.STYLE_FAMILIES}}
    return value in known.get(slot, set())


def apply_photo_terms(scan: dict, photo_terms, warnings: list[str], override: bool = False) -> list[str]:
    """Fill the slots of a ``match_text`` scan that the brief text leaves open with agreed photo terms.

    The brief always wins: a slot the text names keeps its word and the
    photo term is only noted. ``override`` is for a brief without any style
    text, whose default text is itself an assumption: there the photo terms
    replace the default text's words. A photo family fills only the
    family (the floor / walls / light the family implies still count as assumed).
    Each use goes to ``scan["matched"]`` as ``photo:<file>:<term>`` and to
    ``warnings``; terms outside the vocabulary are ignored with a warning.
    Returns the ``photo:...`` entries added.
    """
    used: list[str] = []
    filled: set = set()
    for term in photo_term_list(photo_terms):
        slot, value = term.get("slot"), term.get("value")
        files = [str(f) for f in (term.get("files") or ([term["file"]] if term.get("file") else []))] or ["?"]
        where = ", ".join(files)
        if slot not in PHOTO_SLOTS or not _photo_value_known(slot, value):
            warnings.append(f"ignored photo term {slot}={value!r} from {where} (not in the vocabulary)")
            continue
        if slot in filled:
            warnings.append(f"ignored photo term {slot}={value} from {where} (a photo term already gave {slot})")
            continue
        if scan[slot] is not None and not override:
            if scan[slot] != value:
                warnings.append(f"photo: {slot} {value} from {where} not used (the brief names {scan[slot]})")
            continue
        if scan[slot] is not None and scan[slot] != value:
            warnings.append(f"photo: {slot} {value} from style photo {where} replaces {scan[slot]} of the default "
                            f"style text (no style in the brief)")
        else:
            warnings.append(f"photo: {slot} {value} from style photo {where} (the brief names no {slot}; "
                            f"both models agree)")
        scan[slot] = value
        filled.add(slot)
        for f in files:
            entry = f"photo:{f}:{value}"
            scan["matched"].append(entry)
            used.append(entry)
    return used


# --------------------------------------------------------------------------
# Profile assembly
# --------------------------------------------------------------------------

def _exterior_words_look(slot: str, phrase: str) -> tuple[Optional[dict], list[str]]:
    """``({material, colour}, notes)`` of the brief's ``exterior:`` words for one slot; None when no material word."""
    notes: list[str] = []
    d = _new_draft()
    ph = _Phrase(phrase, d, notes, set())
    lc = _normalise(phrase)
    frag = Frag(lc, 0, len(lc))
    look = None
    if slot == "window_frame":
        look = _frame_look(ph, frag) or None
    elif slot == "door":
        look = _door_look(ph, frag)
        look = {"material": look.get("material"), "colour": look.get("colour")} if look.get("material") else None
    elif _h_exterior(ph, frag, slot, "brief"):
        look = {k: d["exterior"][slot][k] for k in ("material", "colour")}
    return look, notes


def _look(slug: Optional[str], colour: Optional[str], source: str, assumed: bool) -> dict:
    return {"material": slug, "asset": asset_of(slug), "colour": colour, "source": source, "assumed": assumed}


def _exterior_slots(d: dict, profile: dict, fallback: dict, exterior_words: dict, warnings: list[str]) -> dict:
    """The six exterior slots: the brief's ``exterior:`` words, else the style text's own exterior words, else the
    interior window frames / doors the style names, else ``style.exterior_fallback`` (assumed, listed once)."""
    words = {k: str(v).strip() for k, v in (exterior_words or {}).items() if isinstance(v, str) and v.strip()}
    for slot in words:
        if slot not in FIN.EXTERIOR_SLOTS:
            warnings.append(f"ignored exterior word '{slot}: {words[slot]}' (slots: {', '.join(FIN.EXTERIOR_SLOTS)})")
    out: dict = {}
    assumed: list[str] = []
    for slot in FIN.EXTERIOR_SLOTS:
        look = None
        if slot in words:
            found, notes = _exterior_words_look(slot, words[slot])
            warnings.extend(notes)
            if found and found.get("material"):
                look = _look(found["material"], found.get("colour"), "brief", False)
            else:
                warnings.append(f"unmatched exterior.{slot} '{words[slot]}': no known {slot} material word")
        if look is None and slot in d["exterior"]:
            e = d["exterior"][slot]
            look = _look(e["material"], e["colour"], "brief", False)
        if look is None and slot in ("window_frame", "door") and d[slot if slot == "door" else "window_frame"]:
            inside = profile[slot]
            look = _look(inside["material"], inside.get("colour"), "style", False)
        if look is None:
            fb = fallback.get(slot)
            if fb == "interior":
                inside = profile[slot]
                look = _look(inside["material"], inside.get("colour"), "fallback", True)
                assumed.append(f"{slot} as inside ({inside['material']})")
            else:
                fb = fb if isinstance(fb, dict) else {}
                colour = fb.get("colour")
                if colour == "walls":
                    colour = profile["walls"].get("colour")
                look = _look(fb.get("material"), colour, "fallback", True)
                assumed.append(f"{slot} {fb.get('material')}" + (f" in {colour}" if colour else ""))
        out[slot] = look
    if assumed:
        warnings.append("assumed: exterior " + ", ".join(assumed) + " from style.exterior_fallback of wenart/defaults.yaml "
                        "(no word for them in the brief)")
    return out


def profile_from_text(text: str, defaults: Optional[dict] = None, photo_terms=None, *,
                      photo_over_text: bool = False, exterior_words: Optional[dict] = None) -> dict:
    """The style profile of one brief text (see module docstring); ``photo_terms``: see ``apply_photo_terms``;
    ``exterior_words``: the brief's ``exterior:`` block (``{facade, roof, window_frame, door, paving, garden}``)."""
    defaults = defaults or _defaults_or_builtin()
    family_defaults = dict(defaults["style"]["fallback"])
    fallback = copy.deepcopy(defaults["style"].get("exterior_fallback") or BUILTIN_DEFAULTS["style"]["exterior_fallback"])
    scan = match_text(text)
    d = scan["draft"]
    warnings = list(scan["notes"])
    apply_photo_terms(scan, photo_terms, warnings, override=photo_over_text)

    family = scan["family"]
    family_table = dict(V.STYLE_FAMILIES).get(family, {}) if family else {}

    def pick(slot: str) -> str:
        if scan[slot]:
            return scan[slot]
        if slot in family_table:
            warnings.append(f"assumed: {slot} {family_table[slot]} from style family '{family}' (no {slot} word in the brief)")
            return family_table[slot]
        warnings.append(f"assumed: {slot} {family_defaults[slot]} from wenart/defaults.yaml (no {slot} word in the brief)")
        return family_defaults[slot]

    floor = pick("floor")
    walls = pick("walls")
    mood = pick("light")
    floor_colour = d["floor_colour"] if d["floor"] == floor else None
    wall_colour = d["wall_colour"] if d["walls"] == walls else None

    wet_floor = floor if is_wet_safe(floor) else V.WET_FLOOR_DEFAULT
    door_material = floor if _entry(floor).get("kind") == "wood" else V.TRIM_MATERIAL
    light = V.LIGHTING[mood]
    if light["sun_strength"] == 0 and light.get("lamps_on"):
        warnings.append(f"{mood} mood: no sun, the lamps are on (table, floor, pendant and ceiling lights emit)")
    elif light["sun_strength"] == 0:
        warnings.append(f"{mood} mood: no sun; interior lamps are off, renders will be dark")

    if "natural" in d["tags"] and d["furniture"]["wood"] is None:
        wood = O.STYLE_TAGS["natural"]["furniture_wood"]
        d["furniture"]["wood"] = wood
        warnings.append(f"assumed: furniture wood {wood} from the style word 'natural' (no furniture wood word in the brief)")

    accent = None
    if d["wall_accent"]:
        a = d["wall_accent"]
        accent = {"material": a["material"], "asset": asset_of(a["material"]), "colour": a["colour"],
                  "room_types": list(O.ACCENT_ROOM_TYPES), "rule": O.ACCENT_RULE}
        warnings.append(f"accent wall colour {a['colour'] or a['material']}: {O.ACCENT_RULE}")

    wet = d["wet_walls"]
    wet_material = wet.get("material") or V.WET_WALLS_MATERIAL
    wet_params = _entry(wet_material).get("params") or {}
    wet_entry = {"material": wet_material, "asset": asset_of(wet_material),
                 "tile_size_m": wet.get("tile_size_m") or (wet_params.get("tile_size_m") if wet.get("material") else None),
                 "pattern": wet_params.get("pattern") if wet.get("material") else None,
                 "colour": wet.get("colour"), "grout_colour": wet.get("grout_colour")}

    door = d["door"]
    door_entry = {"material": door.get("material") or door_material,
                  "asset": asset_of(door.get("material") or door_material), "style": door.get("style"),
                  "colour": door.get("colour"), "handle": door.get("handle")}
    frame = d["window_frame"]
    frame_material = frame.get("material") or V.WINDOW_FRAME_MATERIAL
    frame_entry = {"material": frame_material, "asset": asset_of(frame_material), "colour": frame.get("colour"),
                   "outside": {"material": frame_material, "colour": frame.get("colour")}}

    cab = d["cabinets"]
    furniture = {"wood": d["furniture"]["wood"], "fabric_colour": d["furniture"]["fabric_colour"],
                 "by_type": d["furniture"]["by_type"], "accents": d["furniture"]["accents"]}

    profile = {
        "source_text": text,
        "family": family,
        "floor": {"material": floor, "asset": asset_of(floor), "colour": floor_colour},
        "walls": {"material": walls, "asset": asset_of(walls), "colour": wall_colour},
        "wall_accent": accent,
        "ceiling": {"material": V.CEILING_MATERIAL, "colour": d["ceiling_colour"]},
        "wet_floor": {"material": wet_floor, "asset": asset_of(wet_floor),
                      "colour": floor_colour if wet_floor == floor else None},
        "wet_walls": wet_entry,
        "trim": {"material": V.TRIM_MATERIAL, "colour": d["trim_colour"]},
        "door": door_entry,
        "window_frame": frame_entry,
        "cabinets": {"front_style": cab.get("front_style"), "colour": cab.get("colour"), "handle": cab.get("handle"),
                     "worktop": cab.get("worktop"), "wood": cab.get("wood")},
        "furniture": furniture,
        "decor": copy.deepcopy(d["decor"]),
        "exterior": {},
        "exterior_fallback": fallback,
        "lighting": {"hdri": light["hdri"], "sun_elevation_deg": light["sun_elevation_deg"],
                     "sun_azimuth_deg": light["sun_azimuth_deg"], "sun_strength": light["sun_strength"],
                     "colour_temperature_k": light["colour_temperature_k"], "mood": mood},
        "colours": d["colours"],
        "matched_terms": scan["matched"],
        "unmatched_terms": scan["unmatched"],
        "warnings": warnings,
    }
    profile["exterior"] = _exterior_slots(d, profile, fallback, exterior_words, warnings)
    return profile


def style_texts(brief: Optional[dict]) -> list[str]:
    """The style texts of a brief: ``style`` first, then every entry of ``styles``."""
    texts: list[str] = []
    if brief:
        if isinstance(brief.get("style"), str) and brief["style"].strip():
            texts.append(brief["style"].strip())
        for entry in brief.get("styles") or []:
            if isinstance(entry, str) and entry.strip():
                texts.append(entry.strip())
    return texts


def profiles_from_brief(brief: Optional[dict], defaults: Optional[dict] = None, photo_terms=None) -> list[dict]:
    """One profile per style text of the brief; the default text when there is none.

    ``photo_terms`` (agreed terms of the style photos, §6) fill only the
    slots each text does not name; without any style text they replace the
    default text's words. The brief's ``exterior:`` block (docs/milestone10.md §1.3) is read for every profile.
    """
    defaults = defaults or _defaults_or_builtin()
    texts = style_texts(brief)
    ext = (brief or {}).get("exterior") if isinstance((brief or {}).get("exterior"), dict) else None
    if not texts:
        profile = profile_from_text(defaults["style"]["text"], defaults, photo_terms, photo_over_text=True,
                                    exterior_words=ext)
        profile["warnings"].insert(0, "assumed: no style in the brief, default style text from wenart/defaults.yaml")
        return [profile]
    return [profile_from_text(t, defaults, photo_terms, exterior_words=ext) for t in texts]


def profile_from_brief(brief: Optional[dict], defaults: Optional[dict] = None, photo_terms=None) -> dict:
    """The first (or only) profile of the brief (``photo_terms``: see ``profiles_from_brief``)."""
    return profiles_from_brief(brief, defaults, photo_terms)[0]


def default_profile() -> dict:
    """The default profile: the default style text run through the vocabulary.

    Equal to the ``style.profile`` block of ``wenart/defaults.yaml`` (checked
    by tests/test_style.py) but computed, so the asset ids always come from
    the vocabulary and no PyYAML is needed (the scene builder in Blender).
    """
    defaults = _defaults_or_builtin()
    return profile_from_text(defaults["style"]["text"], defaults)


def default_block_yaml() -> str:
    """The ``style.profile`` block of ``wenart/defaults.yaml`` as YAML text (the keys under ``profile:``, indented
    four spaces): paste it there after a change of the tables or of the parser (tests/test_style.py compares it)."""
    import yaml  # lazy: only the tests and this helper need PyYAML

    text = yaml.safe_dump(default_profile(), sort_keys=False, default_flow_style=None, allow_unicode=True, width=118)
    return "\n".join(("    " + ln) if ln else ln for ln in text.rstrip("\n").split("\n"))


# --------------------------------------------------------------------------
# Helpers for the scene builder and the asset fetcher
# --------------------------------------------------------------------------

def is_wet_room(room_type: Optional[str]) -> bool:
    """Bathrooms, WCs and kitchens get the wet-room floor and walls."""
    return room_type in V.WET_ROOM_TYPES


def room_surfaces(profile: dict, room_type: Optional[str]) -> dict:
    """``{"floor": slug, "walls": slug, "ceiling": slug, "wet": bool}`` for a room."""
    wet = is_wet_room(room_type)
    return {"floor": profile["wet_floor" if wet else "floor"]["material"],
            "walls": profile["wet_walls" if wet else "walls"]["material"],
            "ceiling": profile["ceiling"]["material"], "wet": wet}


def material_slugs(profile: dict) -> list[str]:
    """Every material slug of the vocabulary the profile uses: the Milestone 3 slots (floor, walls, ceiling, wet
    rooms, trim, door, window frame) first, then the Milestone 10 ones (accent wall, outside window frame, furniture
    wood, cabinet wood and worktop, pots, exterior looks). A slug of neither vocabulary table (a worktop word) is
    not listed."""
    slots = ("floor", "walls", "ceiling", "wet_floor", "wet_walls", "trim", "door", "window_frame")
    found: list[str] = [profile[slot]["material"] for slot in slots]
    accent = profile.get("wall_accent")
    if accent:
        found.append(accent["material"])
    outside = (profile.get("window_frame") or {}).get("outside") or {}
    found.append(outside.get("material"))
    furniture = profile.get("furniture") or {}
    found.append(furniture.get("wood"))
    cabinets = profile.get("cabinets") or {}
    found.append(cabinets.get("wood"))
    found.append(FIN.CABINET_WORKTOPS.get(cabinets.get("worktop")))
    found.append(FIN.CABINET_HANDLES.get(cabinets.get("handle")))
    for pot in (profile.get("decor") or {}).get("pots") or []:
        found.append(FIN.POT_MATERIALS.get(pot.get("material")))
    for look in (profile.get("exterior") or {}).values():
        if isinstance(look, dict):
            found.append(look.get("material"))
    seen: list[str] = []
    for slug in found:
        if slug and _entry(slug) and slug not in seen:
            seen.append(slug)
    return seen


def assets_in_profile(profile: dict) -> dict:
    """``{"textures": [(source, asset_id, slug), ...], "hdris": [(source, hdri_id)]}``; procedural looks and flat
    metals have no asset and are left out."""
    textures, seen = [], set()
    for slug in material_slugs(profile):
        asset_id = asset_of(slug)
        if asset_id and asset_id not in seen:
            seen.add(asset_id)
            textures.append((source_of(slug), asset_id, slug))
    hdri = profile["lighting"]["hdri"]
    return {"textures": textures, "hdris": [(V.HDRIS.get(hdri, {}).get("source", "polyhaven"), hdri)]}


def write_profiles(profiles: list[dict], out_path: Path) -> list[Path]:
    """Write the first profile to ``out_path`` and the others to ``<stem>_2.json`` ... next to it.

    The set is replaced as a whole: an extra profile this writer made for an earlier brief with more
    styles (``<stem>_<n>.json``, n > the new count) is removed, so no stale profile looks current.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for i, profile in enumerate(profiles):
        path = out_path if i == 0 else out_path.with_name(f"{out_path.stem}_{i + 1}{out_path.suffix}")
        path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(path)
    extra = re.compile(rf"{re.escape(out_path.stem)}_([0-9]+){re.escape(out_path.suffix)}")
    for old in out_path.parent.iterdir():
        m = extra.fullmatch(old.name)
        if m and int(m.group(1)) > max(1, len(profiles)) and old.is_file():
            old.unlink()
    return written
