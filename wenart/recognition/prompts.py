"""One prompt per recognition task for the vision-language models.

The prompts explain the Turkish floor-plan vocabulary in English, name every
field of the answer schema and end with "answer only with JSON". The enum
lists are rendered from ``schemas.py`` so prompt and schema cannot drift
apart (``tests/test_recognition_cpu.py`` checks this).

The models receive one image per call. Boxes are asked for in the 0..1000
normalised frame (see ``schemas.py``). The prompt also states the pixel size
of the image so a model that prefers absolute coordinates has the numbers.

Milestone 7 (docs/milestone7.md §3.3, §3.4): ``symbol_type_prompt(facts)`` (two
crops of one drawn object: the plan around it with a dashed box, then the
object alone with a 1 m bar) and ``room_label_prompt`` (one crop of one raster
room face, a fixed text). The symbol question carries the item's **facts**
(``recognition.symbols.question_facts``, prep pod finding P5): the room's
printed label and type, the drawn footprint size, only the types whose size
range fits that footprint (plus ``unknown`` and ``not_furniture``) and the
similar pieces around it; it says that small symbols drawn on a piece belong to
it and defines the front in image terms. Raster crops (pixel copies of a scan)
get their own image description (every line is ink, text may appear; review
raster-7). The text is a deterministic function of the facts, so it is part of
the request's ``input_sha256``: a changed question makes the stored answers
stale. ``symbol_type_prompt()`` without facts is the generic question (full
list, vector crops) for items that carry none.
"""
from __future__ import annotations

from wenart.recognition import schemas

SYSTEM_PROMPT = (
    "You read Turkish architectural drawings (floor plans, furniture plans, sections) "
    "and answer only with JSON that follows the given schema. Report only what is "
    "visible in the image. Never invent elements. When unsure, lower the confidence."
)

# Turkish words that appear on the drawings, with their English meaning.
VOCABULARY: dict[str, str] = {
    "KAT PLANI": "floor plan",
    "ZEMİN KAT": "ground floor",
    "BODRUM KAT": "basement",
    "1. KAT / 2. KAT": "1st / 2nd floor",
    "MOBİLYA PLANI": "furniture plan",
    "KESİT": "section",
    "GÖRÜNÜŞ": "elevation",
    "VAZİYET PLANI": "site plan",
    "ÖLÇEK 1/100": "scale 1:100",
    "SALON": "living room",
    "YATAK ODASI": "bedroom",
    "EBEVEYN YATAK ODASI": "master bedroom",
    "ÇOCUK ODASI": "children's room",
    "MUTFAK": "kitchen",
    "BANYO": "bathroom",
    "WC": "toilet",
    "HOL / ANTRE / KORİDOR": "hall / entrance hall / corridor",
    "BALKON": "balcony",
    "KİLER / DEPO": "pantry / storage",
    "m²": "square metres (area label after a room name, e.g. 'SALON 24,50 m²')",
    "3,45": "a dimension in metres with a decimal comma (3.45 m)",
}

# Symbol type -> what it looks like on a plan (helps the models map drawings to the enum).
SYMBOL_HINTS: dict[str, str] = {
    "door": "a wall gap with a straight leaf line and a quarter-circle swing arc",
    "window": "two parallel lines inside a wall gap, closed at both ends",
    "bed_double": "a wide rectangle about 1.6 x 2.0 m with a headboard line",
    "bed_single": "a narrow rectangle about 0.9 x 2.0 m with a headboard line",
    "sofa": "a long rectangle about 1.6-2.2 x 0.9 m with a backrest line",
    "armchair": "a square about 0.9 x 0.9 m with a backrest line",
    "table_dining": "a rectangle about 1.6 x 0.9 m, usually with chairs around it",
    "table_coffee": "a small rectangle about 1.0 x 0.6 m in front of a sofa",
    "desk": "a rectangle about 1.4 x 0.7 m with one chair",
    "chair": "a small square about 0.45 x 0.45 m",
    "wardrobe": "a long shallow rectangle about 1.8 x 0.6 m against a wall",
    "kitchen_counter": "a long shallow rectangle about 2.4 x 0.6 m along a kitchen wall",
    "kitchen_island": "a free-standing counter rectangle in the kitchen",
    "fridge": "a square about 0.7 x 0.7 m in the kitchen",
    "stove": "a square about 0.6 x 0.6 m in the kitchen",
    "sink_kitchen": "a rectangle about 0.8 x 0.5 m in the kitchen",
    "washbasin": "a small rectangle about 0.6 x 0.45 m in a bathroom",
    "toilet": "a small rectangle about 0.4 x 0.7 m in a bathroom or WC",
    "shower": "a square about 0.9 x 0.9 m in a bathroom",
    "bathtub": "a rectangle about 1.7 x 0.75 m in a bathroom",
    "tv_unit": "a long shallow rectangle about 1.6 x 0.45 m facing a sofa",
    "bookshelf": "a shallow rectangle about 1.0 x 0.35 m against a wall",
    "nightstand": "a small rectangle about 0.5 x 0.4 m next to a bed",
    "dresser": "a rectangle about 1.2 x 0.5 m in a bedroom",
    "washing_machine": "a square about 0.6 x 0.6 m in a bathroom or kitchen",
    "stair": "a row of parallel, evenly spaced tread lines about 0.25-0.30 m apart, often split by a centre line",
    "side_table": "a small square or round table about 0.4-0.6 m, beside a sofa, armchair or bed",
    "floor_lamp": "a small circle about 0.3-0.5 m, often with rings or spokes, in a corner or beside a sofa",
    "potted_plant": "a circle or star of leaf shapes about 0.3-0.8 m",
    # Milestone 10 (docs/milestone10.md §1.1).
    "sofa_corner": "an L-shaped sofa about 2.2-3.0 m by 1.5-2.2 m: two seat rows meeting at a corner, a backrest along "
                   "the outer sides",
    "chaise": "a long single seat about 0.7 x 1.6 m with a backrest at one short end",
    "ottoman": "a small upholstered square or round seat about 0.4-0.9 m without a backrest",
    "bench": "a long narrow seat about 1.2 x 0.4 m without a backrest, at a bed foot, a table or a hall wall",
    "bar_stool": "a small circle or square about 0.35-0.45 m at a kitchen island or counter",
    "office_chair": "a seat about 0.6 m on a round five-star base, at a desk",
    "console_table": "a narrow table about 1.2 x 0.35 m against a wall, often in a hall",
    "crib": "a small bed about 0.7 x 1.4 m with barred sides, in a child's room",
    "bunk_bed": "a single-bed rectangle about 0.9 x 2.0 m drawn as two beds above each other, often with a ladder",
    "sideboard": "a long low cabinet about 1.6 x 0.45 m against a wall, in a living or dining room",
    "shoe_cabinet": "a slim cabinet about 0.8 x 0.3 m against a wall near the entrance",
    "display_cabinet": "a cabinet with glass doors about 1.0 x 0.4 m against a wall",
    "tall_cabinet": "a tall cabinet about 0.6 x 0.6 m at the end of a kitchen counter run",
    "wall_cabinet": "a kitchen wall cabinet about 0.6 x 0.35 m above the counter, drawn dashed",
    "unknown": "a clear furniture footprint whose type you cannot tell",
}


def _vocabulary_block() -> str:
    lines = ["Turkish words on the drawing and their meaning:"]
    for word, meaning in VOCABULARY.items():
        lines.append(f"- {word}: {meaning}")
    return "\n".join(lines)


def _box_block(width: int, height: int) -> str:
    return (
        f"The image is {width} x {height} pixels. Every box is [x0, y0, x1, y1] with the "
        f"origin at the top-left corner, normalised to 0..{schemas.BOX_MAX} of the image "
        "width (x) and height (y), so x1 > x0 and y1 > y0."
    )


def page_class_prompt(width: int, height: int) -> str:
    classes = ", ".join(schemas.PAGE_CLASSES)
    return "\n\n".join([
        "Task: classify this document page.",
        _vocabulary_block(),
        "Fields of the answer:\n"
        f"- class: one of {classes}. floor_plan = a plan drawing of walls and rooms; "
        "furniture_plan = a plan whose title contains MOBİLYA; section = KESİT; elevation = GÖRÜNÜŞ; "
        "site_plan = VAZİYET; photo_of_plan = a photograph of a paper plan; photo_of_room = a photograph "
        "of a real room; other = none of these.\n"
        "- level_label_raw: the level title exactly as printed (e.g. 'ZEMİN KAT PLANI', '1. KAT PLANI', "
        "'BODRUM KAT PLANI'), or null when there is none.\n"
        "- scale_text: the scale text exactly as printed (e.g. 'ÖLÇEK 1/100'), or null.\n"
        "- confidence: 0..1, how sure you are about the class.",
        _box_block(width, height),
        "Answer only with JSON.",
    ])


def room_labels_prompt(width: int, height: int) -> str:
    return "\n\n".join([
        "Task: list every room label written inside a room of this floor plan.",
        _vocabulary_block(),
        "Fields of the answer: items, a list of objects with\n"
        "- label_raw: the label exactly as printed, including an area suffix if there is one "
        "(e.g. 'YATAK ODASI', 'SALON 24,50 m²').\n"
        "- box: the box around the printed label text.\n"
        "Do not list the page title, the scale text or dimension numbers. Do not translate.",
        _box_block(width, height),
        "Answer only with JSON.",
    ])


def symbols_prompt(width: int, height: int) -> str:
    types = ", ".join(schemas.SYMBOL_TYPES)
    hints = "\n".join(f"- {name}: {hint}" for name, hint in SYMBOL_HINTS.items())
    return "\n\n".join([
        "Task: list every door, window and furniture symbol drawn on this floor plan.",
        _vocabulary_block(),
        f"Allowed values for type: {types}.\nWhat the symbols look like (drawn at scale 1:100):\n{hints}",
        "Fields of the answer: items, a list of objects with\n"
        "- type: one of the allowed values.\n"
        "- box: the box around the whole symbol (for a door include the swing arc).\n"
        "- rotation_deg: rotation of the symbol in degrees counter-clockwise (0 = the long side is horizontal "
        "and the front faces down), or null when you cannot tell.\n"
        "- confidence: 0..1.\n"
        "List each symbol once. Do not list walls, text or dimension lines. Do not invent furniture in empty rooms.",
        _box_block(width, height),
        "Answer only with JSON.",
    ])


def text_items_prompt(width: int, height: int) -> str:
    return "\n\n".join([
        "Task: transcribe every piece of printed text on this drawing page.",
        _vocabulary_block(),
        "Fields of the answer: items, a list of objects with\n"
        "- text: the text exactly as printed, keeping Turkish letters (İ, Ş, Ğ, Ç, Ö, Ü) and decimal commas.\n"
        "- box: the box around that text.\n"
        "Include titles, scale text, room labels and dimension numbers. One item per text line.",
        _box_block(width, height),
        "Answer only with JSON.",
    ])


PROMPTS = {
    "page_class": page_class_prompt,
    "room_labels": room_labels_prompt,
    "symbols": symbols_prompt,
    "text_items": text_items_prompt,
}


def prompt_for(task: str, width: int, height: int) -> str:
    """The user prompt for ``task`` and an image of ``width`` x ``height`` pixels."""
    return PROMPTS[task](width, height)


# --------------------------------------------------------------------------
# Milestone 7: one drawn object (two crops), one raster room face (one crop)
# --------------------------------------------------------------------------

M7_SYSTEM_PROMPT = (
    "You read architectural floor plans (English or Turkish) and answer only with JSON that follows the "
    "given schema. Report only what is visible in the images. Never invent elements. When unsure, lower "
    "the confidence or answer unknown or null."
)

# The question of docs/milestone7.md §3.3, verbatim.
SYMBOL_QUESTION = (
    "Two crops of an architectural floor plan seen from above. The dashed box in the first image (shown alone "
    "in the second, with a 1 m bar) marks one drawn object. Which object type is it?"
)
NOT_FURNITURE_HINT = (
    "lines that are not one piece of furniture or fixed equipment: wall pieces, door swings, window lines, "
    "dimension lines, hatching, text or a rug outline"
)
# Text label sent before each image of a symbol question (vlm_client.build_request ``labels``).
SYMBOL_IMAGE_LABELS: tuple[str, str] = ("Image 1 (plan crop):", "Image 2 (the marked object alone):")


# Milestone 7 refinements of the hints for the symbol question (the Milestone 2 whole-page prompt keeps
# SYMBOL_HINTS as they were): the pieces the prep pod's models confused on real01 (P5).
SYMBOL_TYPE_HINT_UPDATES: dict[str, str] = {
    "nightstand": "a small square or rectangle about 0.4-0.6 m beside the head end of a bed; a lamp (a circle, often "
                  "with a cross) or a telephone may be drawn on it",
    "chair": "a small seat about 0.4-0.5 m with a backrest line along one side; dining chairs stand around a table",
    "armchair": "one upholstered seat about 0.7-1.0 m with a thick backrest and two armrests",
    "table_coffee": "a low table about 0.6-1.2 m, rectangular, square or round, in front of or between sofas",
}
SYMBOL_TYPE_HINTS: dict[str, str] = {**SYMBOL_HINTS, **SYMBOL_TYPE_HINT_UPDATES}

SYMBOL_KINDS: tuple[str, ...] = ("vector", "raster")
# What the two images show: vector crops are drawn in a grey coding; raster crops are pixel copies of the scan.
SYMBOL_IMAGES: dict[str, str] = {
    "vector": "In the first image walls are mid-grey, other drawn objects light grey and the marked object black. "
              "The second image shows the marked object alone, without rotating it; the black bar under it is 1 m "
              "long, so use it to judge the size. There is no text in the images.",
    "raster": "Both images are cut from a scanned or photographed plan, so every line is dark ink: walls are the "
              "thick dark bands, and door swings, window lines, other furniture and printed text or numbers may "
              "appear around the object. Only the object inside the dashed box counts; ignore all text. The second "
              "image shows only the pixels inside the dashed box, without rotating them; the black bar under it is "
              "1 m long, so use it to judge the size.",
}
SYMBOLS_ON_TOP = ("Small symbols drawn on top of the object (a lamp, a telephone, a vase, a plant, pillows, books) "
                  "belong to it: name the type of the whole object they stand on, not of the small symbol.")
FRONT_FIELD = (
    "- front: the edge of the second image that the object's front points to: top (towards the top edge of the "
    "image), right, bottom or left. The front is the side a person faces when using the object: for a bed the foot "
    "end, opposite the headboard and the pillows; for a sofa, armchair or chair the open edge of the seat, opposite "
    "the backrest; for a wardrobe, dresser, nightstand, fridge, stove or washing machine the side with the doors or "
    "drawers; for a counter, desk, washbasin, toilet or bathtub the side where the user stands or sits. Answer none "
    "for an object without a front (a round or square table, a plant, a lamp) or when you cannot tell."
)
# Room type -> plain words for the question (types without plain words are not named).
ROOM_WORDS: dict[str, str] = {
    "living": "a living room", "dining": "a dining room", "bedroom": "a bedroom", "kitchen": "a kitchen",
    "bathroom": "a bathroom", "wc": "a toilet (WC)", "hall": "a hall or corridor", "balcony": "a balcony",
    "storage": "a storage room", "prayer": "a prayer room", "stair": "a stair room",
    "shaft": "a shaft",
}


def _metres(size) -> str:
    return f"{float(size[0]):.2f} x {float(size[1]):.2f} m"


def _fact_lines(facts: dict) -> list[str]:
    """The item's facts as sentences (deterministic: fixed order, sizes in cm)."""
    lines = []
    if facts.get("size_m"):
        lines.append(f"- Its drawn footprint is about {_metres(facts['size_m'])}.")
    if facts.get("shape") == "L":
        lines.append("- Its outline is L-shaped: two arms meeting at a corner (the size is the box around the L).")
    room = facts.get("room")
    if room:
        if room.get("label"):
            words = ROOM_WORDS.get(room.get("type") or "")
            what = f'a room labelled "{room["label"]}" ({words})' if words else f'a space labelled "{room["label"]}"'
        else:
            what = "an unlabelled room"
        lines.append(f"- It is drawn inside {what}.")
    near = facts.get("neighbours") or {}
    similar, next_to, around = near.get("similar"), near.get("next_to"), near.get("around")
    if around and next_to:
        line = (f"- It is one of {around} objects of about the same size and shape drawn around a larger object of "
                f"about {_metres(next_to)}.")
        if similar and similar > around:
            line += f" The room holds {similar} such objects in all."
        lines.append(line)
    else:
        if next_to:
            lines.append(f"- It stands within 0.3 m of a larger drawn object of about {_metres(next_to)}.")
        if similar:
            lines.append(f"- It is one of {similar} objects of about the same size and shape in this room.")
    return lines


def symbol_type_prompt(facts: dict | None = None) -> str:
    """The symbol-type question (§3.3) for one item: ``facts`` = ``{"kind": vector|raster, "choices": [types],
    "size_m": [w, d] | None, "room": {"label", "type"} | None, "neighbours": {"similar", "next_to", "around"} |
    None}`` (``recognition.symbols.question_facts``); None = the generic question (full list, vector crops)."""
    facts = dict(facts or {})
    kind = facts.get("kind") or "vector"
    if kind not in SYMBOL_KINDS:
        raise ValueError(f"symbol question: unknown crop kind {kind!r}")
    choices = list(facts.get("choices") or schemas.SYMBOL_TYPE_CHOICES)
    hints = [f"- {name}: {SYMBOL_TYPE_HINTS[name]}" for name in choices if name in SYMBOL_TYPE_HINTS]
    if schemas.NOT_FURNITURE in choices:
        hints.append(f"- {schemas.NOT_FURNITURE}: {NOT_FURNITURE_HINT}")
    fronts = ", ".join(f for f in schemas.FRONT_CHOICES if f != "none")
    parts = [SYMBOL_QUESTION, SYMBOL_IMAGES[kind]]
    lines = _fact_lines(facts)
    if lines:
        parts.append("What the drawing shows about this object:\n" + "\n".join(lines))
    allowed = f"Allowed values for type: {', '.join(choices)}."
    if facts.get("choices"):
        allowed += ("\nOnly the types whose usual size fits the drawn footprint (15 % tolerance) are offered, plus "
                    "unknown (furniture whose type you cannot tell) and not_furniture.")
    parts += [
        f"{allowed}\nWhat the types look like from above:\n" + "\n".join(hints),
        SYMBOLS_ON_TOP,
        "Fields of the answer:\n"
        "- type: one of the allowed values.\n"
        f"{FRONT_FIELD} The allowed values are {fronts} and none.\n"
        "- confidence: 0..1, how sure you are about the type.\n"
        f"- reason: one short sentence, at most {schemas.REASON_MAX_CHARS} characters, on what you see.",
        "Answer only with JSON.",
    ]
    return "\n\n".join(parts)


def room_label_prompt() -> str:
    """The room-label question for one room face of a raster plan (§3.4)."""
    return "\n\n".join([
        "Task: read the room name printed inside the room in the middle of this crop of a scanned or "
        "photographed floor plan. The crop shows one room and about 0.5 m around it.",
        "Labels may be English (BED ROOM, Kitchen, Bath+ Toilet, Drawing Room) or Turkish (SALON = living room, "
        "YATAK ODASI = bedroom, MUTFAK = kitchen, BANYO = bathroom, ANTRE = entrance hall). Do not translate.",
        "Fields of the answer:\n"
        "- label: the room name exactly as printed; a name printed on two lines is joined with one space; null "
        "when no room name is printed inside this room.\n"
        "- size_text: the room size exactly as printed with the name (e.g. 11' x 10', 14'-0\" X 12'-0\", "
        "3,20 x 4,10), or null.\n"
        "- area_text: the area exactly as printed with the name (e.g. 24,50 m², 110 sq ft), or null.\n"
        f"- box: the box around the printed room name, [x0, y0, x1, y1] normalised to 0..{schemas.BOX_MAX} of "
        "the image width (x) and height (y), origin top-left; null when there is no name.\n"
        "Do not read dimension numbers along the walls, the page title, the scale or names of the "
        "neighbouring rooms at the crop edges.",
        "Answer only with JSON.",
    ])


M7_PROMPTS = {
    "symbol_type": symbol_type_prompt,
    "room_label": room_label_prompt,
}


def m7_prompt(task: str, facts: dict | None = None) -> str:
    """The user prompt of a Milestone 7 per-item task (``symbol_type`` with the item's facts, or ``room_label``)."""
    if task == "symbol_type":
        return symbol_type_prompt(facts)
    return M7_PROMPTS[task]()
