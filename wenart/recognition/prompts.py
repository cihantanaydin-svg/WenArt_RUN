"""One prompt per recognition task for the vision-language models.

The prompts explain the Turkish floor-plan vocabulary in English, name every
field of the answer schema and end with "answer only with JSON". The enum
lists are rendered from ``schemas.py`` so prompt and schema cannot drift
apart (``tests/test_recognition_cpu.py`` checks this).

The models receive one image per call. Boxes are asked for in the 0..1000
normalised frame (see ``schemas.py``). The prompt also states the pixel size
of the image so a model that prefers absolute coordinates has the numbers.
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
