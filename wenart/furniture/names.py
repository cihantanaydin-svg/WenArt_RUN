"""Furniture names written as texts in the plans (26 Oct 2026; the auditor Argus, source ledger check A6).

What: a plan text whose words name a furniture type ("*SIFONIYER", "çamaşır mak.", "Kleiderschrank", "lave-linge") is
source evidence of the documents, like a block name (CLAUDE.md trust order: vector geometry > OCR text and dimensions
> AI vision). Three rules use it, for every project:

1. **Type a drawn footprint** (``infer.type_by_code``, method ``name_text`` right after the block name): an untyped
   drawn footprint with a furniture name text on it or within ``NAME_NEAR_M`` of it gets the named type when the text
   names this piece (``named_piece``: of the drawn pieces whose size fits the named type, it is the one nearest the
   text), the type's product range fits the footprint (``sizes.fits`` with ``NAME_SIZE_TOL``, the block name's
   tolerance), the room may hold the type and a wall type has a side on a wall (``infer.placeable``). Of two name
   texts the nearer one wins; a text whose type does not fit is not used and says why (``infer.name_text_note``, in
   the review entry of the piece).
1b. **Correct an AI type** (``infer.name_text_retypes``; CLAUDE.md "code may retype a drawn piece that the vision
   models typed when its size, room and neighbours clearly say otherwise"): a drawn piece typed by the AI passes or a
   weak code guess (``RETYPE_FROM``) with a name text of another type written on it (within ``NAME_RETYPE_M``)
   takes the named type when it fits the size and the room, ``adjusted_by_ai`` by code with ``drawn_type`` and the
   plan crop kept. A block-named piece or one a reading rule typed is never changed (rule 2 lists the text for review).
2. **Add the named piece** (``add_named_pieces``, run by the pipeline after the last typing): a name text of one type
   with no drawn piece near it (no built piece of the named type within ``NAME_NEAR_M``, no untyped drawn footprint
   the text names and no piece the text is written on) adds that piece ``from_documents`` with the text as evidence
   and an ``inferred`` footprint: the type's default size (``schemas.default_size``) placed by the layout's placer
   (``placer.place`` with the room's drawn pieces as locked obstacles: inside the room, no collision, clearances, door
   swings and walkways, windows, back to the nearest wall when the type needs it) starting at the text. When no valid
   place lies within ``NAME_PLACE_M`` of the text, or the room may not hold the type, or the name is generic ("yatak":
   which bed?) or short ("TV": a socket mark?), the text is listed for review with the reason, never forced
   (``NAMED_REVIEW_KIND``; the critic asks for it until a built piece of the type stands at the text). A text in no
   room but within ``TEXT_ROOM_M`` of one (on its wall line, in a niche) belongs to that room (``room_of_point``).

The texts: the reading records every furniture name text of the read plan pages on the building as
``building["furniture_texts"]`` (``generic.reading.furniture_texts``): ``{"id": entity id, "level_id", "room_id",
"text", "type" | null, "types", "family", "word", "pos": [x, y] building metres, "layer", "file", "page",
"method"}``. A text is a furniture name when ``furniture_name`` says so: not a dimension, title, room label or label
part, level mark, area or size, not a note of more than ``MAX_NAME_WORDS`` words or with a year-like number, not a room
name (a room word of ``building.room_keyword_hits`` outside the furniture phrase: "YATAK" alone is a bedroom, "çalışma
masası" a desk), and ``name_type`` finds one type or one generic name in it. The source ledger classifies its texts
with the same function, so what it checks is what the reading uses.

Zone labels (the same evidence, a room's second label): ``zone_records`` keeps every label of a room whose zone kind
(``zone_kind``, ``ZONE_WORDS``: "YEMEK BÖLÜMÜ", Essbereich, salle à manger, zona pranzo, comedor ...) differs from the
room's type, with its zone (the part of the room nearer to it than to the room's other labels) and the zone's anchors
(``zone_anchors``: ``groups.yaml`` ``room_aliases.content``); ``infer._zone_label_type`` types the anchor drawn there
(``fits_with_partners``: a table drawn with its chairs, ``partner_margin``). ``mentioned_types`` lists the types a free
text names (an AI pass's reason, for ``infer.ai_named_members``).

The vocabulary (``NAME_WORDS``, ``GENERIC_NAMES``): Turkish, English, German, French, Italian and Spanish names,
folded to ASCII lower case (Turkish letters, accents, ß), punctuation and a leading '*' ignored; a phrase matches whole
tokens, a word also with a plural or a Turkish case suffix (``SUFFIXES``: "sifonyeri", "stühle"); the longest phrase
wins ("orta sehpa" over "sehpa", "tek kişilik yatak" over "yatak"); two different types named in one text name
nothing. Words that are also room or drawing words in a language ("bureau", "cocina", "planta", "pianta", "four",
"ada", bare "konsol") are left out.

Why (Argus A6 on real06 L1, 26 Oct 2026): the plan writes "*SIFONIYER" three times and "çamaşır mak." once. The reading
did not read them: f_L1_007 (the text on it) became a desk by the AI tie-break, f_L1_019 stayed an unbuilt unknown,
the master bedroom's dresser was missing, and the empty square f_L1_021 under "çamaşır mak." became a second
washbasin.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from wenart import building as B

NAME_TEXT_METHOD = "name_text"       # the type_method of a piece typed, retyped or added from a name text
NAME_NEAR_M = 1.2                    # a name text and the drawn piece it names: on the footprint or this close to it
NAME_RETYPE_M = 0.15                 # rule 1b: a name text corrects an AI type only written on (or touching) the piece
NAME_PLACE_M = 1.0                   # rule 2: the added piece's centre at most this far from its text
NAME_SIZE_TOL = 0.40                 # = infer.BLOCK_SIZE_TOL: a name text is source evidence like a block name
NAME_ADD_MIN_CHARS = 4               # rule 2: a name this short ("TV", "WC") adds nothing by itself (a socket mark?)
TEXT_ROOM_M = 0.30                   # a text in no room this close to one (on its wall line, in a niche) is in it
MAX_NAME_WORDS = 5                   # a longer text is a note
CONF_NAME_TEXT = 0.7
PRODUCT_MARGIN = 0.15                # two types of a generic name fit about equally (infer's group-member margin)
NAMED_REVIEW_KIND = "named_piece"    # the needs_review kind of a name text rule 2 could not place
RULE_TYPE = "furniture.infer.type_by_code:name_text"
RULE_RETYPE = "furniture.infer.name_text_retypes"
RULE_ADD = "furniture.names.add_named_pieces"
# Rule 1b: the type methods an AI or a weak code guess gave (never a block name, a reading rule or a copy).
RETYPE_FROM = ("ai_two_pass", "inferred", "group_member", "none", None)

# Type families: a name text is matched by a piece of the same family (the source ledger's A6 and rule 1b).
FAMILIES: dict[str, tuple[str, ...]] = {
    "bed": ("bed_single", "bed_double", "bunk_bed", "crib", "bed"),
    "seat": ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "seat"),
    "table": ("table_dining", "table_coffee", "side_table", "console_table", "desk", "table"),
    "storage": ("wardrobe", "dresser", "tall_cabinet", "sideboard", "shoe_cabinet", "display_cabinet", "bookshelf",
                "nightstand", "tv_unit", "wall_cabinet", "storage"),
    "kitchen": ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge"),
    "laundry": ("washing_machine",),
    "bath": ("bathtub", "shower"),
    "basin": ("washbasin",),
    "toilet": ("toilet",),
}
FAMILY_OF = {t: fam for fam, types in FAMILIES.items() for t in types}

# Type -> names (folded: ASCII lower case, words separated by one space). TR, EN, DE, FR, IT, ES.
NAME_WORDS: dict[str, tuple[str, ...]] = {
    "bed_double": ("cift kisilik yatak", "cift kisilik", "double bed", "queen bed", "king bed", "queen size",
                   "king size", "doppelbett", "ehebett", "lit double", "lit 2 places", "letto matrimoniale",
                   "letto doppio", "cama doble", "cama matrimonial", "yatak cift", "bed double"),
    "bed_single": ("tek kisilik yatak", "tek kisilik", "single bed", "twin bed", "einzelbett", "lit simple",
                   "lit 1 place", "letto singolo", "cama individual", "cama sencilla", "yatak tek", "bed single"),
    "bunk_bed": ("ranza", "bunk bed", "etagenbett", "hochbett", "lits superposes", "lit superpose", "letto a castello",
                 "litera"),
    "crib": ("besik", "bebek yatagi", "crib", "babybett", "gitterbett", "berceau", "lit bebe", "lit de bebe", "culla",
             "cuna"),
    "sofa_corner": ("kose koltuk", "kose koltugu", "kose takimi", "l koltuk", "corner sofa", "sectional sofa",
                    "sectional", "ecksofa", "wohnlandschaft", "canape d angle", "divano angolare", "sofa esquinero",
                    "sofa rinconera", "rinconera"),
    "sofa": ("kanepe", "koltuk takimi", "uclu koltuk", "ikili koltuk", "3 lu koltuk", "2 li koltuk", "cekyat", "sofa",
             "couch", "settee", "loveseat", "canape", "divano", "divan"),
    "armchair": ("berjer", "tekli koltuk", "armchair", "arm chair", "easy chair", "lounge chair", "sessel",
                 "fauteuil", "poltrona", "sillon", "butaca"),
    "chaise": ("sezlong", "chaise longue", "chaise lounge", "chaiselongue", "meridienne", "tumbona", "dormeuse"),
    "ottoman": ("puf", "pouf", "pouffe", "ottoman", "footstool", "hocker", "poggiapiedi", "reposapies"),
    "bench": ("bench", "sitzbank", "bank", "banc", "banquette", "panca", "panchina", "banco"),
    "chair": ("sandalye", "chair", "dining chair", "stuhl", "chaise", "sedia", "silla"),
    "office_chair": ("ofis koltugu", "ofis sandalyesi", "calisma sandalyesi", "calisma koltugu", "office chair",
                     "desk chair", "burostuhl", "drehstuhl", "burosessel", "chaise de bureau", "fauteuil de bureau",
                     "sedia da ufficio", "silla de oficina", "silla de escritorio"),
    "bar_stool": ("bar taburesi", "bar sandalyesi", "bar tabure", "tabure", "bar stool", "barstool", "counter stool",
                  "barhocker", "tabouret de bar", "tabouret", "sgabello", "taburete", "taburete de bar"),
    "table_dining": ("yemek masasi", "yemek masa", "dining table", "dinner table", "esstisch", "table a manger",
                     "table de salle a manger", "tavolo da pranzo", "mesa de comedor", "mesa comedor"),
    "table_coffee": ("orta sehpa", "orta sehpasi", "coffee table", "couchtisch", "wohnzimmertisch", "sofatisch",
                     "table basse", "tavolino", "tavolino da salotto", "mesa de centro", "mesa baja"),
    "side_table": ("yan sehpa", "yan sehpasi", "side table", "end table", "beistelltisch", "table d appoint",
                   "bout de canape", "tavolino laterale", "mesa auxiliar", "mesa lateral"),
    "console_table": ("konsol masasi", "konsol sehpa", "dresuar", "console table", "konsolentisch", "table console",
                      "consolle", "consola"),
    "desk": ("calisma masasi", "calisma masa", "bilgisayar masasi", "ders masasi", "desk", "writing desk",
             "computer desk", "schreibtisch", "scrivania"),
    "nightstand": ("komodin", "komidin", "gece masasi", "gece sehpasi", "nightstand", "night stand", "bedside table",
                   "bedside cabinet", "night table", "nachttisch", "nachtschrank", "nachtkastchen", "table de chevet",
                   "chevet", "comodino", "mesita de noche", "mesilla de noche", "mesilla"),
    "dresser": ("sifonyer", "sifoniyer", "dresser", "chest of drawers", "kommode", "commode", "comoda", "cassettiera",
                "cajonera"),
    "wardrobe": ("gardirop", "gardirob", "gardrop", "gardrob", "elbise dolabi", "giysi dolabi", "gomme dolap",
                 "wardrobe", "closet", "kleiderschrank", "armoire", "penderie", "placard", "armadio", "guardaroba",
                 "armario", "ropero"),
    "shoe_cabinet": ("ayakkabilik", "ayakkabi dolabi", "portmanto", "shoe cabinet", "shoe rack", "schuhschrank",
                     "meuble a chaussures", "scarpiera", "zapatero"),
    "sideboard": ("bufe", "buffet", "sideboard", "credenza", "anrichte", "aparador", "vaisselier", "madia"),
    "display_cabinet": ("vitrin", "vitrine", "display cabinet", "china cabinet", "vetrina", "vitrina"),
    "tall_cabinet": ("boy dolabi", "kiler dolabi", "tall cabinet", "pantry cabinet", "hochschrank", "vorratsschrank"),
    "bookshelf": ("kitaplik", "kitapligi", "bookshelf", "bookcase", "book shelf", "bucherregal", "regal", "etagere",
                  "libreria", "estanteria", "scaffale"),
    "tv_unit": ("tv unitesi", "tv unite", "tv sehpasi", "tv sehpa", "tv konsolu", "tv konsol", "televizyon unitesi",
                "televizyon", "tv unit", "tv stand", "tv cabinet", "tv console", "tv board", "media unit", "lowboard",
                "tv schrank", "meuble tv", "mobile tv", "porta tv", "mueble tv", "mueble de tv", "tv"),
    "kitchen_counter": ("tezgah", "mutfak tezgahi", "alt dolap", "bulasik makinesi", "bulasik mak", "bulasik",
                        "counter", "worktop", "dishwasher", "arbeitsplatte", "kuchenzeile", "geschirrspuler",
                        "spulmaschine", "plan de travail", "lave vaisselle", "piano di lavoro", "lavastoviglie",
                        "encimera", "lavavajillas"),
    "kitchen_island": ("mutfak adasi", "kitchen island", "island", "kochinsel", "ilot central", "isola cucina",
                       "isla de cocina"),
    "sink_kitchen": ("evye", "eviye", "kitchen sink", "spule", "spulbecken", "evier", "lavello", "fregadero"),
    "stove": ("ocak", "set ustu ocak", "ankastre ocak", "firin", "ankastre firin", "stove", "cooker", "hob", "oven",
              "herd", "kochfeld", "backofen", "cuisiniere", "plaque de cuisson", "piano cottura", "forno", "horno"),
    "fridge": ("buzdolabi", "buz dolabi", "fridge", "refrigerator", "freezer", "kuhlschrank", "gefrierschrank",
               "refrigerateur", "frigo", "frigorifero", "nevera", "frigorifico"),
    "washing_machine": ("camasir makinesi", "camasir mak", "kurutma makinesi", "kurutma mak", "washing machine",
                        "washer", "dryer", "tumble dryer", "waschmaschine", "trockner", "lave linge", "seche linge",
                        "lavatrice", "asciugatrice", "lavadora", "secadora"),
    "toilet": ("klozet", "asma klozet", "toilet", "toilet bowl", "wc", "toilette", "inodoro"),
    "washbasin": ("lavabo", "washbasin", "wash basin", "hand basin", "basin", "vanity", "waschbecken", "waschtisch",
                  "lavandino", "lavamanos"),
    "shower": ("dus", "dus teknesi", "dus kabini", "shower", "shower tray", "dusche", "duschwanne", "douche", "doccia",
               "ducha", "plato de ducha"),
    "bathtub": ("kuvet", "jakuzi", "jacuzzi", "bathtub", "bath tub", "bath", "badewanne", "baignoire", "vasca",
                "vasca da bagno", "banera"),
    "floor_lamp": ("lambader", "abajur", "floor lamp", "standing lamp", "stehlampe", "stehleuchte", "lampadaire",
                   "piantana", "lampada da terra", "lampara de pie"),
    "potted_plant": ("saksi", "saksi bitkisi", "potted plant", "pot plant", "topfpflanze", "zimmerpflanze",
                     "plante en pot", "pianta in vaso", "planta en maceta", "maceta"),
}
# Generic names: (family, the types they may be, names). The size, the room and the product distance decide (rule 1);
# a generic name never adds a piece (rule 2: which one?).
GENERIC_NAMES: tuple[tuple[str, tuple[str, ...], tuple[str, ...]], ...] = (
    ("bed", ("bed_double", "bed_single"), ("yatak", "yatagi", "bed", "bett", "lit", "letto", "cama")),
    ("seat", ("sofa", "armchair"), ("koltuk", "koltugu")),
    ("table", ("table_dining", "desk", "table_coffee", "side_table", "console_table"),
     ("masa", "masasi", "table", "tisch", "tavolo", "mesa")),
    ("table", ("table_coffee", "side_table"), ("sehpa",)),
    ("storage", ("wardrobe", "tall_cabinet"), ("dolap", "dolabi", "cabinet", "cupboard", "schrank")),
)
# A word of at least SUFFIX_MIN letters also matches with one of these endings (a plural, a Turkish case or
# possessive: "sifonyeri", "komodinler", "stühle" -> "stuhle"); shorter words only with a plural "s" / "es".
SUFFIXES = ("s", "es", "i", "u", "si", "su", "ler", "lar", "leri", "lari", "e", "n", "in", "un")
PLURALS = ("s", "es")
SUFFIX_MIN = 4
NOT_NAME_ROLES = ("dimension", "title", "scale", "room_label")
YEAR_RE = re.compile(r"^\d{4,}$")
_SPECIAL = str.maketrans({"ß": "ss", "ø": "o", "æ": "ae", "œ": "oe", "ł": "l"})


def family(ftype: Optional[str]) -> Optional[str]:
    """The family of a type (``FAMILIES``), the type itself when it has none."""
    if not ftype:
        return None
    return FAMILY_OF.get(ftype, ftype)


def tokens(text) -> list[str]:
    """Folded tokens: Turkish letters and accents to ASCII, lower case, every non-alphanumeric character (a leading
    '*', dots, hyphens) a separator."""
    folded = B.fold_ascii(str(text or "").translate(_SPECIAL))
    return [t for t in re.split(r"[^a-z0-9]+", folded) if t]


def _word_ok(tok: str, word: str) -> bool:
    if tok == word:
        return True
    ends = SUFFIXES if len(word) >= SUFFIX_MIN else PLURALS
    return any(tok == word + s for s in ends)


def _entries():
    for ftype, words in NAME_WORDS.items():
        for w in words:
            yield w, ftype, (ftype,), family(ftype)
    for fam, types, words in GENERIC_NAMES:
        for w in words:
            yield w, None, types, fam


def _matches(toks: list[str]) -> list[tuple[int, int, int, str, Optional[str], tuple, str]]:
    """Every name of the vocabulary found in ``toks``: ``(start, end, chars, phrase, type, types, family)``, overlaps
    resolved longest first."""
    cands = []
    for phrase, ftype, types, fam in _entries():
        words = phrase.split()
        n = len(words)
        for i in range(len(toks) - n + 1):
            if all(_word_ok(toks[i + k], words[k]) for k in range(n)):
                cands.append((i, i + n, len(phrase), phrase, ftype, types, fam))
    out, taken = [], set()
    for c in sorted(cands, key=lambda c: (-c[2], c[0], c[3])):
        span = set(range(c[0], c[1]))
        if span & taken:
            continue
        taken |= span
        out.append(c)
    return sorted(out, key=lambda c: c[0])


def name_type(text) -> Optional[dict]:
    """The furniture a text names: ``{"type": a type | None (a generic name), "types": the types it may be,
    "family", "word": the name found, "span": (first, last token)}``, or None when it names none or names two
    different things ("YATAK + KOMODIN")."""
    toks = tokens(text)
    if not toks:
        return None
    found = _matches(toks)
    if not found:
        return None
    kinds = {(c[4], c[5]) for c in found}
    if len(kinds) != 1:
        return None
    c = max(found, key=lambda c: (c[2], -c[0]))
    return {"type": c[4], "types": tuple(c[5]), "family": c[6], "word": c[3], "span": (c[0], c[1])}


def ledger_type(text) -> Optional[str]:
    """The type a text names, or its family for a generic name (the source ledger's A6 matches families)."""
    hit = name_type(text)
    if hit is None:
        return None
    return hit["type"] or hit["family"]


def _room_word_outside(text: str, hit: dict) -> bool:
    """True when a room word of the text (``building.room_keyword_hits``) is not part of the furniture phrase found: the
    text is a room name ("YATAK" alone is a bedroom; "ÇALIŞMA MASASI" is a desk, its room word inside the phrase)."""
    turkish, english = B.room_keyword_hits(text)
    if not (turkish or english):
        return False
    toks = tokens(text)
    first, last = hit["span"]
    inside = toks[first:last]
    if len(inside) < 2:
        return True
    for keyword, _room in list(turkish) + list(english):
        kw = tokens(keyword)
        if not kw:
            continue
        if not any(t.startswith(kw[0]) for t in inside):
            return True
    return False


def furniture_name(row: dict) -> Optional[dict]:
    """The furniture a plan text names (``name_type``) when the text is a furniture name and nothing else: not a
    dimension, title, scale or room label, not a part of a label block, not a level mark, an area or a size, at most
    ``MAX_NAME_WORDS`` words without a year-like number, and no room name; else None. ``row``: ``{"text", "role",
    "label_part", "tag"}`` (a ``source_items`` text row)."""
    from wenart import units as U
    from wenart.levels import marks as MK

    text = str(row.get("text") or "").strip()
    if not text or row.get("role") in NOT_NAME_ROLES or row.get("label_part"):
        return None
    toks = tokens(text)
    if not toks or len(toks) > MAX_NAME_WORDS or any(YEAR_RE.match(t) for t in toks):
        return None
    if MK.parse_mark(text) is not None or (MK.is_mark_tag(row.get("tag")) and MK.read_mark(text, bare=True)):
        return None
    if U.parse_area(text) is not None:
        return None
    hit = name_type(text)
    if hit is None or _room_word_outside(text, hit):
        return None
    return hit


def mentioned_types(text) -> list[str]:
    """26 Oct 2026 (``infer.ai_named_members``): every furniture type a free text names ("likely a bathtub or shower"
    -> bathtub, shower; a generic name gives its types), in text order, each once."""
    out: list[str] = []
    for c in _matches(tokens(text)):
        for t in c[5]:
            if t not in out:
                out.append(t)
    return out


# --------------------------------------------------------------------------
# Zone labels: a second label inside a room ("YEMEK BÖLÜMÜ" in the salon) names the zone around it
# --------------------------------------------------------------------------

# Zone words (folded, TR / EN / DE / FR / IT / ES) -> the room kind of ``groups.yaml`` ``room_aliases.content`` whose
# anchors the zone holds (dining: the dining table; living: the sofa; kitchen: the counter run; bedroom: the bed;
# other: the desk).
ZONE_WORDS: dict[str, tuple[str, ...]] = {
    "dining": ("yemek", "dining", "dinette", "essbereich", "essplatz", "essecke", "esszimmer", "salle a manger",
               "coin repas", "zona pranzo", "sala da pranzo", "comedor"),
    "living": ("salon", "oturma", "yasama", "living", "lounge", "sitting", "wohnbereich", "wohnzimmer", "sejour",
               "salle de sejour", "soggiorno", "zona giorno", "sala de estar", "estar"),
    "kitchen": ("mutfak", "kitchen", "kitchenette", "kuche", "kochnische", "kochbereich", "cuisine", "coin cuisine",
                "cucina", "angolo cottura", "cocina"),
    "bedroom": ("yatak", "sleeping", "schlafbereich", "schlafzimmer", "coin nuit", "zona notte", "dormitorio"),
    "other": ("calisma", "study", "office", "work area", "arbeitsbereich", "arbeitsecke", "coin bureau",
              "zona studio", "estudio"),
}
ZONE_SAME_M = 0.05                   # two label points this close are one label (read on two pages)


def zone_kind(text) -> Optional[str]:
    """The room kind a zone label names (``ZONE_WORDS``), None when it names none or two ("MUTFAK VE YEMEK")."""
    toks = tokens(text)
    kinds = set()
    for kind, words in ZONE_WORDS.items():
        for phrase in words:
            ws = phrase.split()
            if any(all(_word_ok(toks[i + k], ws[k]) for k in range(len(ws))) for i in range(len(toks) - len(ws) + 1)):
                kinds.add(kind)
                break
    return kinds.pop() if len(kinds) == 1 else None


def zone_anchors(kind: Optional[str]) -> list[str]:
    """The anchor types of a zone kind: the types ``groups.yaml`` ``room_aliases.content`` gives that kind."""
    from wenart.furniture import groups as GR

    content = dict(GR.room_aliases().get("content") or {})
    return [t for t, k in content.items() if k == kind]


def _half_plane(p, q, reach: float = 1000.0):
    """The half plane of the points nearer ``p`` than ``q`` (a large polygon)."""
    from shapely.geometry import Polygon

    mx, my = (p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0
    ux, uy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    vx, vy = -uy, ux
    return Polygon([(mx + vx * reach, my + vy * reach), (mx + vx * reach - ux * reach, my + vy * reach - uy * reach),
                    (mx - vx * reach - ux * reach, my - vy * reach - uy * reach), (mx - vx * reach, my - vy * reach)])


def zone_records(building: dict, room: dict, rows: list[dict], file: Optional[str] = None) -> list[dict]:
    """The zone labels of a room: of the label rows standing in it (``{"id", "text", "label", "pos"}``: the first name
    run of each label block), every one whose zone kind (``zone_kind``) differs from the room's type and has anchors
    (``zone_anchors``), with its zone: the part of the room nearer to this label than to the room's other labels (its
    own label included). ``{"id", "level_id", "room_id", "text", "kind", "anchors", "pos", "zone", "file"}``."""
    from shapely.geometry import Polygon

    poly = Polygon(room["polygon"])
    if not poly.is_valid:
        poly = poly.buffer(0)
    points: list[tuple[float, float]] = []
    for r in rows:
        p = (float(r["pos"][0]), float(r["pos"][1]))
        if not any(math.dist(p, q) <= ZONE_SAME_M for q in points):
            points.append(p)
    own = {" ".join(tokens(room.get(k))) for k in ("label", "label_raw") if room.get(k)}
    out, seen = [], []
    for r in rows:
        label = str(r.get("label") or r.get("text") or "")
        kind = zone_kind(label)
        p = (float(r["pos"][0]), float(r["pos"][1]))
        if kind is None or kind == room.get("room_type") or " ".join(tokens(label)) in own:
            continue
        if any(math.dist(p, q) <= ZONE_SAME_M for q in seen):
            continue
        anchors = zone_anchors(kind)
        if not anchors:
            continue
        cell = poly
        for q in points:
            if math.dist(p, q) > ZONE_SAME_M:
                cell = cell.intersection(_half_plane(p, q))
        if cell.is_empty:
            continue
        if cell.geom_type != "Polygon":
            cell = max(getattr(cell, "geoms", [cell]), key=lambda g: g.area)
        seen.append(p)
        out.append({"id": r.get("id"), "level_id": room.get("level_id"), "room_id": room["id"], "text": label,
                    "kind": kind, "anchors": anchors, "pos": [round(p[0], 3), round(p[1], 3)],
                    "zone": [[round(x, 3), round(y, 3)] for x, y in list(cell.exterior.coords)[:-1]], "file": file})
    return out


def zones_of(building: dict, room_id: Optional[str]) -> list[dict]:
    """The zone labels of a room (``building["zone_labels"]``)."""
    return [z for z in building.get("zone_labels") or [] if isinstance(z, dict) and z.get("room_id") == room_id
            and len(z.get("zone") or []) >= 3]


def zone_of(building: dict, piece: dict) -> Optional[dict]:
    """The zone label whose zone holds the piece's footprint centre, or None."""
    from shapely.geometry import Point, Polygon

    c = (piece.get("footprint") or {}).get("center")
    if not c:
        return None
    pt = Point(float(c[0]), float(c[1]))
    for z in zones_of(building, piece.get("room_id")):
        if Polygon(z["zone"]).buffer(1e-6).contains(pt):
            return z
    return None


def zone_types_elsewhere(building: dict, piece: dict) -> set:
    """27 Oct 2026 (real06's salon: a 1.52 x 0.78 m sofa in the seating area, typed "a dining table in YEMEK BÖLÜMÜ" by
    one AI pass): the anchor types of the labelled zones of the piece's room that do not hold it (a dining table where
    the documents put the dining area elsewhere in the room): never its type. Empty without zone labels."""
    here = zone_of(building, piece)
    out: set = set()
    for z in zones_of(building, piece.get("room_id")):
        if here is not None and z.get("id") == here.get("id"):
            continue
        out |= set(z.get("anchors") or zone_anchors(z.get("kind")))
    if here is not None:
        out -= set(here.get("anchors") or zone_anchors(here.get("kind")))
    return out


def partner_margin(ftype: str) -> float:
    """How far partners drawn around an anchor reach out of it: the deepest partner placed ``around`` the anchor in
    ``groups.yaml`` (the chairs of a dining table, 0.45 m), 0 for an anchor without such partners."""
    from wenart.furniture import groups as GR

    out = 0.0
    for template in GR.load_groups().values():
        if ftype not in ((template.get("anchor") or {}).get("types") or ()):
            continue
        for p in template.get("partners") or []:
            if p.get("place") == "around":
                out = max([out] + [float(s[1]) for s in p.get("sizes") or [] if len(s) >= 2])
    return out


def fits_with_partners(ftype: str, piece: dict, tol: float = NAME_SIZE_TOL) -> bool:
    """The piece's size fits ``ftype`` (``fits_size``), or does once the partners drawn around it are taken off
    (``partner_margin`` on every side: CLAUDE.md "a table footprint that includes its chairs")."""
    from wenart.furniture import sizes as SZ

    if fits_size(ftype, piece, tol):
        return True
    m = partner_margin(ftype)
    size = [float(v) for v in (piece.get("footprint") or {}).get("size") or []]
    if m <= 0 or len(size) < 2 or min(size[:2]) - 2 * m <= 0:
        return False
    return SZ.fits(ftype, [size[0] - 2 * m, size[1] - 2 * m], tol)


def name_chars(text_record: dict) -> int:
    """The letters of the name a text record holds (``word`` without spaces)."""
    return len(str(text_record.get("word") or "").replace(" ", ""))


# --------------------------------------------------------------------------
# Texts on the building
# --------------------------------------------------------------------------

def texts_of(building: dict, level_id: Optional[str] = None) -> list[dict]:
    """The building's furniture name texts (``building["furniture_texts"]``), of one level when given."""
    return [t for t in building.get("furniture_texts") or [] if isinstance(t, dict) and t.get("pos")
            and (level_id is None or t.get("level_id") == level_id)]


def room_of_point(building: dict, level_id: Optional[str], pos) -> Optional[str]:
    """The room of a text: the room of its level that holds the point, else the nearest one within ``TEXT_ROOM_M`` (a
    name written on the wall line or in a niche); None when there is none."""
    from shapely.geometry import Point, Polygon

    pt = Point(float(pos[0]), float(pos[1]))
    best = None
    for r in building.get("rooms") or []:
        if r.get("level_id") != level_id or len(r.get("polygon") or []) < 3:
            continue
        poly = Polygon(r["polygon"])
        if not poly.is_valid:
            poly = poly.buffer(0)
        if poly.contains(pt):
            return r["id"]
        d = poly.distance(pt)
        if d <= TEXT_ROOM_M + 1e-9 and (best is None or (d, r["id"]) < best):
            best = (d, r["id"])
    return best[1] if best else None


def _poly(piece: dict):
    from wenart.furniture import placer

    try:
        return placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None


def text_distance(text: dict, piece: dict) -> float:
    """From the text's position to the piece's footprint (0 on it)."""
    from shapely.geometry import Point

    poly = _poly(piece)
    if poly is None:
        return float("inf")
    return float(poly.distance(Point(float(text["pos"][0]), float(text["pos"][1]))))


def _centre_distance(text: dict, piece: dict) -> float:
    c = (piece.get("footprint") or {}).get("center") or (1e9, 1e9)
    return math.dist((float(c[0]), float(c[1])), (float(text["pos"][0]), float(text["pos"][1])))


def _same_room(text: dict, piece: dict) -> bool:
    """A text in a room names only pieces of that room; a text in no room may name any piece near it."""
    return not (text.get("room_id") and piece.get("room_id") and text["room_id"] != piece["room_id"])


def candidate_piece(piece: dict) -> bool:
    """A drawn piece a name text can name: from the documents, with a footprint, not recorded as something else (a rug
    outline, a detail, a column, not furniture), not a stair."""
    return (piece.get("source") == "from_documents" and bool(piece.get("footprint"))
            and not piece.get("inferred_as") and not piece.get("not_furniture") and piece.get("type") != "stair")


def fits_size(ftype: str, piece: dict, tol: float = NAME_SIZE_TOL) -> bool:
    from wenart.furniture import sizes as SZ

    size = [float(v) for v in (piece.get("footprint") or {}).get("size") or []]
    return len(size) >= 2 and SZ.fits(ftype, size[:2], tol)


def named_piece(building: dict, text: dict) -> Optional[dict]:
    """The drawn piece a name text names: of the drawn pieces of its level and room within ``NAME_NEAR_M`` whose size
    fits a type the text names (``NAME_SIZE_TOL``), the one nearest the text (its footprint, then its centre, then
    the id); None when no such piece stands there."""
    best = None
    for f in building.get("furniture") or []:
        if f.get("level_id") != text.get("level_id") or not candidate_piece(f) or not _same_room(text, f):
            continue
        d = text_distance(text, f)
        if d > NAME_NEAR_M + 1e-9 or not any(fits_size(t, f) for t in text.get("types") or ()):
            continue
        key = (round(d, 4), round(_centre_distance(text, f), 4), str(f.get("id")))
        if best is None or key < best[0]:
            best = (key, f)
    return best[1] if best else None


def texts_near(building: dict, piece: dict) -> list[tuple[float, dict]]:
    """``(distance, text)`` of the name texts on or within ``NAME_NEAR_M`` of a piece's footprint (its level, not in
    another room), nearest first."""
    out = []
    for t in texts_of(building, piece.get("level_id")):
        if not _same_room(t, piece):
            continue
        d = text_distance(t, piece)
        if d <= NAME_NEAR_M + 1e-9:
            out.append((round(d, 4), t))
    return sorted(out, key=lambda x: (x[0], str(x[1].get("id"))))


def used_by(building: dict, text: dict) -> list[dict]:
    """The pieces whose evidence names the text (its entity id)."""
    tid = text.get("id")
    out = []
    for f in building.get("furniture") or []:
        for ev in f.get("evidence") or []:
            if isinstance(ev, dict) and tid and tid in str(ev.get("entity") or "").split(","):
                out.append(f)
                break
    return out


def named_near(building: dict, text: dict) -> Optional[dict]:
    """A built piece of the named type (of the named family for a generic name) on or within ``NAME_NEAR_M`` of the
    text (its level and room): the text names it, nearest first; None when there is none."""
    near = []
    for f in building.get("furniture") or []:
        if f.get("level_id") != text.get("level_id") or f.get("build") is False or not f.get("footprint"):
            continue
        same = family(f.get("type")) == text.get("family") if text.get("type") is None else \
            f.get("type") == text.get("type")
        if not same or not _same_room(text, f):
            continue
        d = text_distance(text, f)
        if d <= NAME_NEAR_M + 1e-9:
            near.append((round(d, 4), str(f.get("id")), f))
    return min(near, key=lambda x: x[:2])[2] if near else None


def describe(text: dict) -> str:
    """``'*SIFONIYER' (TEXT:29ABD3)``."""
    return f"{text.get('text')!r} ({text.get('id')})"


def text_evidence(text: dict, confidence: float = 0.9) -> dict:
    """The evidence entry of the text itself (the documents' name: vector text, or OCR on a scan)."""
    ev = {"file": text.get("file") or "building.json", "page": text.get("page"), "layer": text.get("layer"),
          "entity": text.get("id"), "method": text.get("method") or "vector", "confidence": confidence,
          "text": f"furniture name text {text.get('text')!r} at ({text['pos'][0]:.2f}, {text['pos'][1]:.2f}) m"}
    return {k: v for k, v in ev.items() if v is not None}


# --------------------------------------------------------------------------
# Rule 2: a name text with no drawn piece near it adds the named piece
# --------------------------------------------------------------------------

def _next_piece_id(building: dict, level_id: str) -> str:
    prefix = f"f_{level_id}_"
    used = [int(str(f["id"])[len(prefix):]) for f in building.get("furniture") or []
            if str(f.get("id", "")).startswith(prefix) and str(f["id"])[len(prefix):].isdigit()]
    return f"{prefix}{max(used, default=0) + 1:03d}"


def _obstacles(building: dict, room: dict) -> list:
    """The room's drawn pieces as locked obstacles: the built floor pieces and the untyped drawn footprints (a piece the
    documents draw is never covered by an added one)."""
    from wenart.furniture import infer as INF
    from wenart.furniture import placer, schemas

    out = []
    for f in building.get("furniture") or []:
        if f.get("room_id") != room["id"] or not f.get("footprint") or schemas.off_floor(f):
            continue
        built = f.get("build") is not False and f.get("type") not in (None, "unknown")
        if not (built or INF.untyped_drawn(f)):
            continue
        try:
            out.append(placer.drawn_piece(f, len(out)))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def place_named(building: dict, room: dict, text: dict) -> tuple[Optional[dict], str]:
    """Rule 2: ``(footprint {"center", "size", "rotation_deg", "front_deg", "moved_m"}, "")``: the type's default size
    placed by the placer at the text (``placer.place`` with the room's drawn pieces locked; a wall type snapped to the
    nearest wall first); ``(None, why)`` when no place passing every check lies within ``NAME_PLACE_M`` of the text."""
    from wenart import geometry as G
    from wenart.furniture import infer as INF
    from wenart.furniture import placer, schemas

    ftype = text["type"]
    pos = (float(text["pos"][0]), float(text["pos"][1]))
    ctx = placer.room_context(building, room)
    size = tuple(schemas.default_size(ftype))
    wall = INF.needs_wall(ftype) or schemas.orientation_rule(ftype)["back"] in ("wall", "wall_or_group")
    obstacles = _obstacles(building, room)
    start, rotation = pos, 0.0
    if wall:
        probe = placer.Piece(ftype, pos, 0.0, size, True)
        snapped = placer.snap_to_wall(probe, ctx, others=obstacles)
        if snapped is not None:
            start, rotation = snapped[0], snapped[1]
    proposal = [{"type": ftype, "center": [start[0], start[1]], "rotation_deg": rotation, "size": list(size),
                 "against_wall": wall, "reason": f"named by {describe(text)}"}]
    result = placer.place(proposal, ctx, obstacles=obstacles)
    if not result.pieces:
        why = ", ".join(result.dropped[0]["failed"]) if result.dropped else "no position"
        return None, f"no place in {room['id']} passes the checks ({why})"
    p = result.pieces[0]
    failed = placer.failed_checks(result.checks[0]) if result.checks else []
    if failed:
        return None, f"the nearest place in {room['id']} fails {', '.join(failed)}"
    d = math.dist(p.center, pos)
    if d > NAME_PLACE_M + 1e-9:
        return None, (f"the nearest place that passes every check in {room['id']} is {d:.2f} m from the text (more "
                      f"than {NAME_PLACE_M:g} m)")
    rot = round(G.normalise_angle(p.rotation_deg), 3)
    fp = {"center": [round(p.center[0], 4), round(p.center[1], 4)], "size": [float(p.size[0]), float(p.size[1])],
          "rotation_deg": rot}
    return dict(fp, front_deg=round(G.front_direction_deg(rot), 3), moved_m=round(d, 3)), ""


def _review(text: dict, reason: str) -> dict:
    return {"id": text.get("id"), "kind": NAMED_REVIEW_KIND, "reason": reason, "room_id": text.get("room_id"),
            "level_id": text.get("level_id"), "text": text.get("text"), "type": text.get("type"),
            "pos": list(text.get("pos") or [])}


def add_named_pieces(building: dict) -> dict:
    """Rule 2 (module docstring), applied to ``building`` in place: ``{"added": [piece ids], "review": [needs_review
    entries], "warnings": [lines]}``. Nothing is done for a text a piece uses or that a built piece of the named type
    stands near (``named_near``), nor for a text that names an untyped drawn footprint (``named_piece``: rule 1 typed it
    or its own review entry says why not). A text written on a typed piece of another type that rule 1b did not change
    (within ``NAME_RETYPE_M``) is listed for review: the documents disagree with it, nothing is added."""
    from wenart.furniture import schemas

    rooms = {r["id"]: r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    out = {"added": [], "review": [], "warnings": []}
    for text in sorted(texts_of(building), key=lambda t: (str(t.get("level_id")), str(t.get("id")))):
        if used_by(building, text) or named_near(building, text) is not None:
            continue
        what = text.get("type") or f"{text.get('family')} ({' / '.join(text.get('types') or ())})"
        at = f"({describe(text)}) at ({text['pos'][0]:.2f}, {text['pos'][1]:.2f}) m on {text.get('level_id')}"
        owner = named_piece(building, text)
        if owner is not None and owner.get("type") in (None, "unknown"):
            continue                 # the untyped drawn piece the text names: typed by rule 1 or listed with the reason
        if owner is not None and text_distance(text, owner) <= NAME_RETYPE_M + 1e-9:
            reason = (f"the documents name a {what} {at}, written on the drawn {owner.get('type')} {owner.get('id')} "
                      f"(typed by {owner.get('type_method') or 'the reading'}); the name and the type disagree and "
                      f"code did not change it (a block name or a reading rule typed it, or the named type does not "
                      f"fit its size or room): not added")
            out["review"].append(_review(text, reason))
            out["warnings"].append(f"{text.get('id')}: {reason}")
            continue
        head = f"the documents name a {what} {at} and no drawn {what} stands there"
        room = rooms.get(text.get("room_id") or "")
        if text.get("type") is None:
            why = f"a generic name ('{text.get('word')}'): which {text.get('family')} is not said"
        elif name_chars(text) < NAME_ADD_MIN_CHARS:
            why = f"a name of {name_chars(text)} letters ('{text.get('word')}') may be a mark (a socket), not a piece"
        elif room is None:
            why = "the text stands in no room"
        elif text["type"] not in schemas.allowed_types(room.get("room_type"), room.get("room_subtype")):
            why = f"a {room.get('room_type')} room holds no {text['type']}"
        else:
            fp, why = place_named(building, room, text)
            if fp is not None:
                piece = _new_piece(building, room, text, fp)
                building.setdefault("furniture", []).append(piece)
                room["has_documented_furniture"] = True
                out["added"].append(piece["id"])
                out["warnings"].append(f"{piece['id']}: {piece['inferred_reason']}")
                continue
        reason = f"{head}: not added: {why}"
        out["review"].append(_review(text, reason))
        out["warnings"].append(f"{text.get('id')}: {reason}")
    if out["review"]:
        listed = {(n.get("id"), n.get("kind")) for n in building.get("needs_review") or [] if isinstance(n, dict)}
        building.setdefault("needs_review", []).extend(n for n in out["review"] if (n["id"], n["kind"]) not in listed)
    return out


def _new_piece(building: dict, room: dict, text: dict, fp: dict) -> dict:
    from wenart.furniture import schemas

    ftype = text["type"]
    reason = (f"{ftype} from the documents: the name text {describe(text)} at ({text['pos'][0]:.2f}, "
              f"{text['pos'][1]:.2f}) m with no drawn piece near it; footprint inferred: the type's default size "
              f"{fp['size'][0]:.2f} x {fp['size'][1]:.2f} m placed by the placer {fp['moved_m']:.2f} m from the text"
              + (", back to the nearest wall" if schemas.orientation_rule(ftype)["back"] in ("wall", "wall_or_group")
                 else "") + ", every check passed")
    inferred_ev = {"file": text.get("file") or "building.json", "entity": text.get("id"), "method": "inferred",
                   "confidence": CONF_NAME_TEXT, "rule": RULE_ADD, "text": reason,
                   "name_text": {"id": text.get("id"), "text": text.get("text"), "pos": list(text["pos"])}}
    return {"id": _next_piece_id(building, room["level_id"]), "level_id": room["level_id"], "room_id": room["id"],
            "type": ftype, "type_raw": text.get("text"), "source": "from_documents",
            "footprint": {k: fp[k] for k in ("center", "size", "rotation_deg")}, "front_deg": fp["front_deg"],
            "height": schemas.HEIGHTS.get(ftype), "asset": None, "status": "unverified",
            "evidence": [text_evidence(text), inferred_ev], "type_method": NAME_TEXT_METHOD, "type_candidates": [],
            "build": True, "inferred": True, "inferred_reason": reason, "footprint_inferred": True,
            "named_by": text.get("id")}
