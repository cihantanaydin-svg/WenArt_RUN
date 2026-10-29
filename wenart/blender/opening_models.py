"""Library doors and windows for the outer openings (user request of 24 Oct 2026: "start using outside doors ... there
are new windows you can try to use").

What: ``plan(building, levels, outlines, extras, mode)`` -> ``{opening id: entry}``: for every door and window on the
outside of the building, the audited library model of its category, scaled into the opening (side by side in
``panels`` for a long window or a wide glazed door), or nothing (the parametric opening stays). ``load_extras(path)``
reads the catalogue's ``extras`` (the 3D Warehouse doors and windows).

Why: the parametric doors and windows are plain frames and slabs; the library holds about 90 audited doors and 50
windows (``wenart/furniture/catalog_library.json`` extras, types ``door`` and ``window``).

How (pure; ``opening_build.build_library_opening`` makes the Blender objects):
- categories: ``entrance`` (the main entrance of ``site.entrances``, else the first door at grade), ``door`` (any
  other outside door narrower than ``WIDE_DOOR_M``), ``glazed_door`` (wider), ``terrace_door`` (a door the architect
  marked ``outside_door``: to a terrace or balcony room; glazed, one leaf) and ``window``;
- candidates: audit ``keep`` / ``fix``, not rated low by the audit's vision check (``site_models.vision_quality``),
  usable in the licence mode, a plausible size for the category (``SIZES``), no
  pack, set or inside door (``INSIDE_WORDS``) in the title, depth under ``MAX_DEPTH_M``; ranked textured first, the
  title's category words (``WORDS``), ``keep`` before ``fix``, then the smallest proportion error over the
  category's openings, then the id;
- one model per category, so a building's windows match: an opening takes the category's model when one panel's
  proportions (panel width over height) lie within ``ASPECT_TOL`` (a log ratio) of the model's, with the number of
  panels (1 .. ``MAX_PANELS``) that fits best and its height lies within ``MAX_SCALE`` of the model's (a scaled-down
  model gets toy frames); else (until 26 Oct 2026) the next ranked candidate that fits, (since 26 Oct 2026) another
  member of the same family, else none (the parametric opening).
Every entry records the asset (id, file, frame fields, licence), ``panels``, ``category``, ``aspect_error``, the
``outward`` plan direction and the reason; the build marks the object ``inferred`` (the documents draw the opening, not its product).

26 Oct 2026 (user on real06, a Scandinavian house: "The house needs to make sense and needs to look very stylish"; a
glazed door with a busy black-and-white lattice, dark six-panel doors on the facade, one black-framed traditional sash
window among white sliding ones):

- What: the house's style picks the openings. ``OPENING_LOOK`` says per style family what a designer puts in
  (``FAMILY_LOOK``: Scandinavian, Japandi, modern, minimal, contemporary -> ``light``: clear glass, no or few glazing
  bars, a flush or glazed leaf; industrial -> ``industrial``: glazing bars allowed; classic, rustic, Mediterranean ->
  ``period``: panelled leaves and bars allowed). ``look_fit`` leaves a model out when its title names the other look
  (``PERIOD_WORDS``, a panelled leaf ``_panelled``, or ``MODERN_WORDS``), when half or more of its audited styles are
  the look's ``avoid`` styles, or (with the files, ``glb_panes``) when its glass is patterned (an image on a glass
  material) or divided by glazing bars (``BARS_MIN_LITES`` lites and ``BARS_PER_M2`` per square metre) where the look
  wants clear glass; it ranks the rest (0 the house's own family, 1 a style of the look, 2 unknown, 3 a minority of
  avoided styles). The audited styles reach the catalogue's extras in ``load_extras`` (the audit's vision answers,
  ``growth_entries.apply_audit_styles``).
- One door and window language: the openings of a category take one model family (``family_key``: one model, or the
  size and colour variants of one series), the family whose best model ranks first by style, then by the audit's
  vision quality (``audit_quality``, 28 Oct 2026), then covers the most
  openings, then the old order. An opening no member fits stays the parametric opening in the style's finish (listed
  in ``notes``) instead of a model of another family; ``opening_build`` paints every frame in the style's finish.
- Why: the choice ranked textured models first and fell back to any model that fitted, so the house got a
  traditional sash beside modern sliders and dark panelled doors in a Scandinavian facade.

28 Oct 2026 (user: "I want better doors inside the house and the outside, I am not liking that much the models used at
the moment, some variation is needed", then "find the best models"; real04 had "Aluminium Casement Window" on 26
windows and "Front Door" models on every outside door, real06 "Single Casement Window" x35):

- What, the sources: the HSSD doors and windows (``wenart.assets.hssd_openings``: Floorplanner product series in many
  sizes, audited with the opening question) join the 3D Warehouse extras. Their structured fields are read before the
  title words: ``model_role`` (the audit's role: entrance, outside, inside, garage, window), ``model_glazing`` (none,
  clear, bars, patterned), ``model_leaves``, ``model_operation`` (the audit's, then the HSSD table's, then the title),
  ``model_handle_side``; ``family_key`` takes a model's ``series`` (the variants of one product). ``load_extras``
  reads the openings audit too (``AUDIT_FILES``; ``audit_openings``).
- What, variation by role in one language: the entrance takes a statement door (``is_statement``: the audit's
  entrance role or a front-door title, before the coverage), the outside service doors take another family than the
  entrance, terrace doors stay glazed, the windows one family; a category whose openings open two ways (a French and a
  sliding door) gives each opening a member that opens its way (``op_ok``); among families equal on every rank the
  house's seed (``house_seed``: its project id) picks one, so two houses of one style do not get the same products
  (``_choose_family``).
- What, inside doors: ``inside_records`` (the interior doors: rooms on both sides, the room each opens into) and
  ``plan_inside`` plan library models for them (category ``inside_door``), one family per role (``inside_role``, the
  door style of ``looks.door_look``: ``glazed`` into the living rooms, ``solid`` to the private rooms, ``sliding``
  where the drawing slides it), the glazed role preferring the solid role's series, never a facade family; each entry
  faces the room the door opens into (``outward``), is centred in its wall (``inside``), mirrored to a drawn hinge side
  (``hinge_mirror``) and gets the lever handles when its model shows none (``add_handles``). A door no model fits stays
  the parametric door (``notes``).
- What, the checks: ``door_variety_problems`` (pure) finds a house whose doors are all one model, an inside door model
  on the facade and an entrance without a statement door.
- Why: after the title filters about ten 3D Warehouse models fitted an entrance and one a terrace door, all rated 3 of
  5; the inside doors were parametric slabs.

29 Oct 2026 (user on real06 run 20261028-154514-full: "Better door models needed"; lesson UL89; 5 of its 13 doors were
the parametric door, 7 one 3D Warehouse model, none an HSSD model; real04 run 20261028-183611-full: a "bathroom door"
with a vent grille on 12 doors, the HSSD entrance, inside doors and windows parametric):

- What, the cause: ``asset_of`` left the credit fields ``source_url`` and ``via`` out of the build record, so the
  build's licence rule refused every HSSD (CC BY-NC 4.0) door and window the plan chose and built the parametric one.
  The record carries every credit field (``CREDIT_FIELDS``) and the plan never chooses a model the build would refuse
  (``build_refusal``).
- What, the choice: a door whose leaf the audit's opening question never saw ranks after the doors it saw
  (``look_fit``, ``LEAF_UNKNOWN_RANK``); a door named for one kind of room (``model_rooms``) serves only doors into such
  rooms; a pair of leaves (``is_pair``) takes two leaves of its role's model, mirrored to meet in the middle (``pair``);
  doors of one category that open two ways take a second family for the way the first does not open (``_place``); the
  glazed and terrace doors are not the entrance's family either (``SERVICE_DOORS``) when another of the look fits.
- What, the checks: ``built_doors``, ``door_product_problems`` (model review M20: a planned library door the build did
  not make, a bare parametric door), ``door_model_problems`` (Argus U18: most doors parametric, a door named for another
  room). The parametric door itself is a product of the style family where nothing fits (``looks.door_product``).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import struct
from pathlib import Path
from typing import Optional, Sequence

WIDE_DOOR_M = 1.4
MAX_DEPTH_M = 0.45
ASPECT_TOL = 0.25                  # |log(panel w/h over model w/h)| <= 0.25: about 28 % either way
MAX_SCALE = 1.8                    # the opening's height within 1/1.8 .. 1.8 x the model's (frames keep real sizes)
MAX_PANELS = 8
RANK_STEP = 0.05                   # 25 Oct 2026: the mean proportion error ranks in steps: a few new windows of odd
                                   # proportions no longer swap the building's model (real04: aluminium -> leaded)
SIZES = {                          # (width range, height range) of one model, metres
    "entrance": ((0.75, 1.5), (1.9, 2.8)),
    "door": ((0.65, 1.4), (1.9, 2.7)),
    "glazed_door": ((1.2, 4.0), (1.9, 2.9)),
    "terrace_door": ((0.7, 1.6), (1.9, 2.7)),
    "window": ((0.4, 3.0), (0.4, 2.6)),
    "inside_door": ((0.6, 1.25), (1.9, 2.7)),        # 28 Oct 2026: the interior doors (``plan_inside``)
}
WORDS = {                          # title words that say a model is meant for the category
    "entrance": ("front", "entrance", "entry", "main", "pivot", "exterior"),
    "door": ("front", "entry", "exterior", "door"),
    "glazed_door": ("sliding", "glass", "french", "patio", "folding", "balcony", "terrace"),
    "terrace_door": ("balcony", "glass", "glazed", "french", "patio", "terrace", "lite"),
    "window": ("window", "casement", "sliding", "awning", "tilt"),
    "inside_door": ("interior", "internal", "inside", "room", "flush", "panel", "bedroom", "bathroom", "door"),
}
INSIDE_WORDS = ("interior", "internal", "toilet", "elevator", "japanese", "closet", "wardrobe", "shower", "barn",
                # 28 Oct 2026 (real04 and real06 got a "bathroom door" model on the facade): the rooms an inside door
                # names, and what is no door of a house
                "bathroom", "bedroom", "room door", " wc ", "container")
# 27 Oct 2026: a one-leaf category (entrance, door, terrace door) never takes a model whose title names a sliding
# system ("Lift Slide") or a pair ("Double ...", "Duble"): the build scales one model into the whole opening
PAIR_WORDS = ("slide", "double", "duble", "pair")
NOT_WORDS = {                      # title words that rule a model out of the category (an outer opening)
    "entrance": ("sliding", "folding", "glass", "garage", "pack", "set", "window") + PAIR_WORDS + INSIDE_WORDS,
    "door": ("sliding", "folding", "garage", "pack", "set", "window") + PAIR_WORDS + INSIDE_WORDS,
    # 28 Oct 2026 (real06's French door took a "Front Door" with a glass tag): a front door is no glazed door either
    "glazed_door": ("garage", "pack", "set", "front", "entry", "entrance") + INSIDE_WORDS,
    # 28 Oct 2026 (real04's terrace doors took a "Front Door"): a front or entry door is no terrace door
    "terrace_door": ("garage", "pack", "set", "sliding", "folding", "front", "entry") + PAIR_WORDS + INSIDE_WORDS,
    "window": ("pack", "set", "door", "curtain", "blind", "shutter", "wall"),
    # 28 Oct 2026: an inside door is no front, terrace, garage or lift door and no pair (the build scales one leaf)
    "inside_door": ("front", "entrance", "entry", "exterior", "external", "garage", "patio", "balcony", "terrace",
                    "pack", "set", "window", "shower", "elevator", "container", "security", "storm", "double", "duble",
                    "pair"),
}
NEVER_FLAGS = ("no_derivatives", "unknown")

# 26 Oct 2026: the doors and windows a designer puts in each style family (``wenart.style.vocabulary.STYLE_FAMILIES``;
# "contemporary" as ``details.STYLE_KINDS`` names it). ``styles``: the audited styles that suit the look; ``avoid``: the
# ones that do not; ``not_words``: title words of the other look; ``panelled``: a panelled leaf is out; ``clear_glass``:
# a patterned pane is out; ``bars``: glazing bars allowed; ``leaf`` and ``frames``: what the look builds (the build
# paints every frame in the style's own finish, ``opening_build``).
PERIOD_WORDS = ("colonial", "victorian", "georgian", "edwardian", "regency", "sash", "double hung", "carriage",
                "craftsman", "bungalow", "bungelow", "traditional", "cottage", "arched", "arch ", "leaded",
                "classical", "classic", "rustic", "antique", "ornate", "gothic", "castle", "wrought", "decorative",
                "raised panel", "louver", "louvre", "jali")
MODERN_WORDS = ("aluminium", "aluminum", "frameless", "glass wall", "pivot", "contemporary", "minimal", "modern",
                "industrial", "steel")
GLASS_SYSTEM_WORDS = ("sliding", "slide", "folding", "bifold", "bi-fold", "glass", "contemporary", "modern", "minimal",
                      "pivot", "patio")
LIGHT_STYLES = ("scandinavian", "japandi", "modern", "modern minimal", "minimal", "contemporary")
PERIOD_STYLES = ("classic", "rustic", "mediterranean", "traditional", "ornate")
OPENING_LOOK = {
    "light": {"styles": LIGHT_STYLES, "avoid": PERIOD_STYLES, "not_words": PERIOD_WORDS, "panelled": True,
              "clear_glass": True, "bars": False, "leaf": ("flush", "glazed"),
              "frames": ("white", "black", "light wood", "aluminium")},
    "industrial": {"styles": ("industrial",) + LIGHT_STYLES, "avoid": PERIOD_STYLES, "not_words": PERIOD_WORDS,
                   "panelled": True, "clear_glass": True, "bars": True, "leaf": ("flush", "glazed"),
                   "frames": ("black steel", "dark aluminium")},
    "period": {"styles": ("classic", "rustic", "mediterranean"), "avoid": ("industrial", "minimal", "modern minimal"),
               "not_words": MODERN_WORDS, "panelled": False, "clear_glass": False, "bars": True,
               "leaf": ("panelled", "glazed", "flush"), "frames": ("white", "wood", "dark wood")},
}
FAMILY_LOOK = {"scandinavian": "light", "japandi": "light", "modern": "light", "modern minimal": "light",
               "minimal": "light", "contemporary": "light", "industrial": "industrial", "classic": "period",
               "rustic": "period", "mediterranean": "period"}
BARS_MIN_LITES = 6                 # glazing bars: at least this many lites ...
BARS_PER_M2 = 2.0                  # ... and this many per square metre of the model's face (a French door: 16 / 3.9)
MIN_LITE_M2 = 0.01                 # glass pieces smaller than this are no lite (a peephole, a sliver)
AUDIT_FILES = ("results/library/audit/3dwh/audit.json",      # audits whose vision answers style the extras
               "results/library/audit/openings/audit.json")  # 28 Oct 2026: the HSSD doors and windows (the pod's p4)


def load_extras(path, audits: Optional[Sequence] = None) -> list[dict]:
    """The catalogue's ``extras`` (doors, windows, ... of the 3D Warehouse layer); [] when the file or key is missing.
    26 Oct 2026: an entry that still carries the ``neutral`` placeholder takes the styles of its audit's vision answer
    (``audits``: audit result files; default ``AUDIT_FILES`` under the repository of the catalogue), the rule of
    ``growth_entries.apply_vision_fields``: the catalogue copy was written before that rule read the extras."""
    p = Path(path)
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    # 27 Oct 2026: a door or window audited with its front along the leaf gets the leaf's face as its front
    extras = [leaf_front(e) if isinstance(e, dict) else e for e in data.get("extras") or []]
    if audits is None:
        parents = p.resolve().parents
        audits = [parents[2] / a for a in AUDIT_FILES] if len(parents) > 2 else []
    for a in audits:
        if not Path(a).is_file():
            continue
        try:
            doc = json.loads(Path(a).read_text(encoding="utf-8"))
            audit_styles(extras, doc)
            audit_quality(extras, doc)
            audit_openings(extras, doc)
        except (OSError, ValueError, TypeError, AttributeError):   # a broken audit file never stops the build
            continue
    return extras


def audit_quality(extras: list, audit_doc: Optional[dict]) -> int:
    """The audit's vision quality (1-5) of each extra as ``audit_quality`` (pure, in place; 28 Oct 2026, user: "I want
    better doors inside the house and the outside, I am not liking that much the models used at the moment"): the
    choice ranks the best-looking models first (``_rank_key``). Returns how many entries got one."""
    answers = {str(it["id"]): (it.get("vision") or {}).get("quality") for it in (audit_doc or {}).get("items") or []
               if isinstance(it, dict) and it.get("id") and isinstance(it.get("vision"), dict)}
    n = 0
    for e in extras:
        q = answers.get(str(e.get("id"))) if isinstance(e, dict) else None
        if isinstance(q, int) and e.get("audit_quality") is None:
            e["audit_quality"] = q
            n += 1
    return n


OPENING_FIELDS = ("role", "operation", "leaves", "glazing", "leaf", "handle_side")     # = ask.OPENING_FIELDS


def audit_openings(extras: list, audit_doc: Optional[dict]) -> int:
    """The opening question's answer (``OPENING_FIELDS``) of each door or window as ``opening_vision`` where the
    catalogue has none (pure, in place; 28 Oct 2026; the rule of ``growth_entries.opening_fields``, kept here so the
    build does not import the growth code). Returns how many entries got one."""
    answers = {str(it["id"]): it["vision"] for it in (audit_doc or {}).get("items") or []
               if isinstance(it, dict) and it.get("id") and isinstance(it.get("vision"), dict)}
    n = 0
    for e in extras:
        a = answers.get(str(e.get("id"))) if isinstance(e, dict) else None
        if not a or isinstance(e.get("opening_vision"), dict):
            continue
        seen = {f: a[f] for f in OPENING_FIELDS if f in a}
        if seen:
            e["opening_vision"] = dict(seen, note="the audit's vision answer (the opening question), at load")
            n += 1
    return n


AUDIT_STYLE_MAX = 3             # = growth_entries.STYLE_MAX: styles taken from one vision answer


def audit_styles(extras: list, audit_doc: Optional[dict]) -> int:
    """The audit's vision styles (at most ``AUDIT_STYLE_MAX``) on the extras that carry only the ``neutral``
    placeholder (pure, in place; the rule of ``growth_entries.apply_vision_fields``, kept here so the build does not
    import the library growth code). Returns how many entries were styled."""
    answers = {str(it["id"]): it["vision"] for it in (audit_doc or {}).get("items") or []
               if isinstance(it, dict) and it.get("id") and isinstance(it.get("vision"), dict)}
    n = 0
    for e in extras:
        if not isinstance(e, dict) or e.get("id") not in answers:
            continue
        if [x for x in e.get("styles") or [] if x != "neutral"]:
            continue
        seen = [x for x in answers[e["id"]].get("styles") or [] if isinstance(x, str) and x and x != "neutral"]
        if not seen:
            continue
        e["styles"] = sorted(set(seen[:AUDIT_STYLE_MAX]))
        e["style_note"] = f"the audit's vision answer names {seen[:AUDIT_STYLE_MAX]} (26 Oct 2026, at load)"
        n += 1
    return n


def style_family(style) -> Optional[str]:
    """The style family of a style (``style.json``'s ``family``) or a family name, lower case; None without one."""
    fam = style.get("family") if isinstance(style, dict) else style
    fam = str(fam or "").strip().lower()
    return fam or None


def look_of(style) -> Optional[dict]:
    """``OPENING_LOOK`` of a style (with its ``name`` and the ``family``), None for no or an unknown family."""
    fam = style_family(style)
    name = FAMILY_LOOK.get(fam or "")
    return dict(OPENING_LOOK[name], name=name, family=fam) if name else None


def entry_styles(entry: dict) -> list[str]:
    """The audited styles of a model without the ``neutral`` placeholder, lower case, each once, in order."""
    out = []
    for s in entry.get("styles") or []:
        s = str(s or "").strip().lower()
        if s and s != "neutral" and s not in out:
            out.append(s)
    return out


def _word(title: str, words) -> Optional[str]:
    """The first of ``words`` that starts a word of ``title`` (" arch " matches "arched", never "search")."""
    for w in words:
        if re.search(r"(?<![a-z0-9])" + re.escape(w.strip()) + (r"(?![a-z0-9])" if w.endswith(" ") else ""), title):
            return w.strip()
    return None


def _panelled(title: str) -> bool:
    """A title that names a panelled leaf ("6 Panel", "2 Panels", "panelled"); "3-panel" or "4 Panel" of a sliding or
    folding glass system counts its leaves, not raised panels."""
    if not re.search(r"panel", title) or re.search(r"\d\s*-\s*panel", title):
        return False
    return _word(title, GLASS_SYSTEM_WORDS) is None


LEAF_UNKNOWN_RANK = 2              # 29 Oct 2026: a door whose leaf the audit never saw ranks as a look unknown
# the doors whose leaf only the audit can tell (a glazed or terrace door is mostly glass: its panes and its glass share
# are read from the file, ``_checked``)
LEAF_CATEGORIES = ("entrance", "door", "inside_door")


def look_fit(entry: dict, look: Optional[dict], panes: Optional[dict] = None,
             category: Optional[str] = None) -> tuple[Optional[int], str]:
    """``(rank, why)`` of a model for the house's look (pure): rank None = left out, else 0 (the house's own family
    among its audited styles, none avoided), 1 (a style of the look, none avoided), 2 (no audited style), 3 (a style of
    the look and a minority of avoided ones). ``panes``: ``glb_panes`` of its file (None: not judged). Without a look
    every model ranks 0.

    29 Oct 2026 (user: "Better door models needed"; real06's judge: "identical, heavy, traditional pine panels" on
    its bedroom doors): a door model (``LEAF_CATEGORIES``) whose leaf the audit's opening question never saw (no
    ``opening_vision.leaf``: the 3D Warehouse doors) ranks at best ``LEAF_UNKNOWN_RANK``: its styles came from a
    vision answer that never asked for the leaf ("Residential Interior Door", four raised panels and a knob, read
    "minimal, modern, scandinavian", ranked 0 and took every solid door of a Scandinavian house before the HSSD flush
    doors the opening question saw). It stays usable where no audited door fits. ``LEAF_CATEGORIES``: the doors
    whose leaf matters (a glazed or terrace door is judged by its glass from the file)."""
    rank, why = _look_rank(entry, look, panes, category)
    if rank is not None and look is not None and category in LEAF_CATEGORIES and rank < LEAF_UNKNOWN_RANK \
            and model_vision(entry).get("leaf") is None:
        return LEAF_UNKNOWN_RANK, why + "; its leaf not seen by the audit's opening question: after the doors it saw"
    return rank, why


def _look_rank(entry: dict, look: Optional[dict], panes: Optional[dict] = None,
               category: Optional[str] = None) -> tuple[Optional[int], str]:
    """``look_fit`` before the leaf rule of 29 Oct 2026."""
    if look is None:
        return 0, "no style family: every look"
    title = _title(entry)
    w = _word(title, look["not_words"])
    if w:
        return None, f"its title says {w!r}: not the {look['family']} look"
    if look["panelled"] and (_panelled(title) or model_vision(entry).get("leaf") == "panelled"):
        return None, f"a panelled leaf: not the {look['family']} look"
    glazing = model_glazing(entry)
    if look["clear_glass"] and glazing == "patterned" and category in GLAZED:
        return None, f"patterned glass (the audit): the {look['family']} look wants clear glass"
    if not look["bars"] and glazing == "bars":
        return None, f"glazing bars (the audit): the {look['family']} look wants no or few bars"
    styles = entry_styles(entry)
    avoid = [s for s in styles if s in look["avoid"]]
    if styles and 2 * len(avoid) >= len(styles):
        return None, f"audited styles {styles}: mostly {', '.join(avoid)}, not the {look['family']} look"
    if panes:
        if look["clear_glass"] and panes.get("patterned") and category in GLAZED:
            return None, f"patterned glass (an image on its glass): the {look['family']} look wants clear glass"
        if not look["bars"] and int(panes.get("lites") or 0) >= BARS_MIN_LITES \
                and float(panes.get("per_m2") or 0.0) >= BARS_PER_M2:
            return None, (f"glazing bars ({panes['lites']} lites, {panes['per_m2']:.1f} per m2): the "
                          f"{look['family']} look wants no or few bars")
    good = [s for s in styles if s in look["styles"]]
    if look["family"] in styles and not avoid:
        return 0, f"audited styles {styles} name {look['family']}"
    if good and not avoid:
        return 1, f"audited styles {styles} suit the {look['family']} look"
    if not avoid:
        return 2, f"audited styles {styles or ['none']}: look unknown"
    return 3, f"audited styles {styles}: partly {', '.join(avoid)}"


FAMILY_DROP = ("white", "black", "grey", "gray", "timber", "oak", "walnut", "wood", "wooden", "door", "doors", "panel",
               "panels", "leaf", "leaves")


def family_key(entry: dict) -> str:
    """The model family of a door or window (pure): the variants of one series share it ("Window1 1" and "Window1 3",
    "Valdi - Folding Sliding Door - 3 Door White" and "- 4 Door Timber": the title without its numbers, colours and
    leaf counts, the first two parts of a "brand - product - variant" title); a title with nothing to strip is its own
    family (seven different "Front Door" models are seven families). 28 Oct 2026: a model with a ``series`` (the HSSD
    Floorplanner variants of one product, ``hssd:218``) is that series."""
    series = entry.get("series") or _opening_rec(entry).get("series")
    if series:
        return f"{entry.get('type')}:series:{series}"
    title = re.sub(r"\[[^\]]*\]", " ", str(entry.get("title") or entry.get("name") or "").lower())
    title = " ".join(title.replace("_", " ").split())
    parts = [p.strip() for p in title.split(" - ") if p.strip()]
    stem = " - ".join(parts[:2]) if len(parts) >= 3 else title
    words = [w for w in re.split(r"\s+", stem) if w]
    kept = [w for w in words if not re.match(r"^\d", w)]
    if len(parts) >= 3:
        tail = [w for w in " ".join(parts[2:]).split() if not re.match(r"^\d", w) and w not in FAMILY_DROP]
        if not tail:
            return f"{entry.get('type')}:{' '.join(kept)}"
        return f"id:{entry.get('id')}"
    if kept != words and kept:
        return f"{entry.get('type')}:{' '.join(kept)}"
    return f"id:{entry.get('id')}"


GLASS_NAME_WORDS = ("glass", "glas", "glazing", "pane", "vidro", "vitre", "cam_", "camlar", "transparent",
                    "translucent", "window_glass")  # = opening_build.GLASS_WORDS
GLAZED = ("window", "glazed_door", "terrace_door")


def glb_glass(path) -> Optional[bool]:
    """Whether a GLB model has a see-through material (pure: the file's JSON chunk): a material named like glass, one
    with a blended alpha under 0.7, or with ``KHR_materials_transmission`` over 0.5. None when the file cannot be
    read. 25 Oct 2026: real04's "Window1 1" (3D Warehouse) has panes painted on an opaque texture: chosen for every
    window it shut the daylight out of the south rooms (+4..+7 EV)."""
    import struct

    try:
        with open(path, "rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] != b"glTF":
                return None
            n, kind = struct.unpack("<II", f.read(8))
            if kind != 0x4E4F534A:                     # "JSON"
                return None
            doc = json.loads(f.read(n).decode("utf-8"))
    except (OSError, ValueError, struct.error):
        return None
    for m in doc.get("materials") or []:
        name = str(m.get("name") or "").lower()
        if any(w in name for w in GLASS_NAME_WORDS):
            return True
        pbr = m.get("pbrMetallicRoughness") or {}
        alpha = (pbr.get("baseColorFactor") or [1, 1, 1, 1])[3:4] or [1.0]
        if m.get("alphaMode") == "BLEND" and float(alpha[0]) < 0.7:
            return True
        trans = ((m.get("extensions") or {}).get("KHR_materials_transmission") or {}).get("transmissionFactor")
        if trans is not None and float(trans) > 0.5:
            return True
    return False


GLAZED_DOOR_MIN_SHARE = 0.45     # a terrace or glazed door model is at least this much glass (25 Oct 2026)


def _glb_json(path) -> Optional[dict]:
    import struct

    try:
        with open(path, "rb") as f:
            head = f.read(12)
            if len(head) < 12 or head[:4] != b"glTF":
                return None
            n, kind = struct.unpack("<II", f.read(8))
            if kind != 0x4E4F534A:                     # "JSON"
                return None
            return json.loads(f.read(n).decode("utf-8"))
    except (OSError, ValueError, struct.error):
        return None


def _glass_material(m: dict) -> bool:
    name = str(m.get("name") or "").lower()
    if any(w in name for w in GLASS_NAME_WORDS):
        return True
    pbr = m.get("pbrMetallicRoughness") or {}
    alpha = (pbr.get("baseColorFactor") or [1, 1, 1, 1])[3:4] or [1.0]
    if m.get("alphaMode") == "BLEND" and float(alpha[0]) < 0.7:
        return True
    trans = ((m.get("extensions") or {}).get("KHR_materials_transmission") or {}).get("transmissionFactor")
    return trans is not None and float(trans) > 0.5


def glb_glass_share(path) -> Optional[float]:
    """The share of a door or window model's face that is glass (pure: the GLB's JSON chunk; 25 Oct 2026, user on
    real04's roof terrace door, a wood door with four small panes: "is the door to the terrace ok?"): the summed
    face areas (the two largest sides of the box) of the glass primitives' position bounds over the model's. None
    when the file cannot be read or holds no bounds."""
    doc = _glb_json(path)
    if doc is None:
        return None
    mats = doc.get("materials") or []
    acc = doc.get("accessors") or []
    glass, lo, hi = 0.0, [math.inf] * 3, [-math.inf] * 3
    for mesh in doc.get("meshes") or []:
        for prim in mesh.get("primitives") or []:
            a = (prim.get("attributes") or {}).get("POSITION")
            if a is None or a >= len(acc) or not acc[a].get("min") or not acc[a].get("max"):
                continue
            mn, mx = [float(v) for v in acc[a]["min"][:3]], [float(v) for v in acc[a]["max"][:3]]
            lo = [min(x, y) for x, y in zip(lo, mn)]
            hi = [max(x, y) for x, y in zip(hi, mx)]
            m = prim.get("material")
            if m is not None and m < len(mats) and _glass_material(mats[m]):
                e = sorted((y - x for x, y in zip(mn, mx)), reverse=True)
                glass += e[0] * e[1]
    if not math.isfinite(lo[0]):
        return None
    e = sorted((y - x for x, y in zip(lo, hi)), reverse=True)
    face = e[0] * e[1]
    return None if face <= 0 else round(min(1.0, glass / face), 3)


# --- the panes of a model (26 Oct 2026) ---------------------------------------------------------------------------

def _glb_parts(path) -> Optional[tuple[dict, bytes]]:
    """``(json, bin)`` chunks of a GLB file; None when it cannot be read."""
    try:
        data = Path(path).read_bytes()
    except OSError:
        return None
    if len(data) < 20 or data[:4] != b"glTF":
        return None
    off, doc, binc = 12, None, b""
    try:
        while off + 8 <= len(data):
            n, kind = struct.unpack_from("<II", data, off)
            off += 8
            chunk = data[off:off + n]
            off += n
            if kind == 0x4E4F534A and doc is None:            # "JSON"
                doc = json.loads(chunk.decode("utf-8"))
            elif kind == 0x004E4942 and not binc:             # "BIN"
                binc = chunk
    except (ValueError, struct.error):
        return None
    return (doc, binc) if isinstance(doc, dict) else None


_FORMATS = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}
_WIDTH = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}


def _accessor(doc: dict, binc: bytes, index) -> Optional[list]:
    """The values of a glTF accessor in the BIN chunk (tuples for vectors, ints / floats for scalars); None for one
    this reader does not take (sparse, quantised, another buffer, out of range)."""
    accs = doc.get("accessors") or []
    if not isinstance(index, int) or not 0 <= index < len(accs):
        return None
    acc = accs[index]
    views = doc.get("bufferViews") or []
    bv_i = acc.get("bufferView")
    if not isinstance(bv_i, int) or not 0 <= bv_i < len(views) or acc.get("sparse"):
        return None
    bv = views[bv_i]
    fmt = _FORMATS.get(acc.get("componentType"))
    width = _WIDTH.get(acc.get("type"))
    if fmt is None or width is None or int(bv.get("buffer", 0)) != 0 or (acc.get("normalized") and fmt[0] != "f"):
        return None
    count = int(acc.get("count") or 0)
    size = fmt[1] * width
    stride = int(bv.get("byteStride") or size)
    base = int(bv.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
    if count <= 0 or base + stride * (count - 1) + size > len(binc):
        return None
    if stride == size:
        flat = struct.unpack_from(f"<{count * width}{fmt[0]}", binc, base)
    else:
        flat = []
        for i in range(count):
            flat.extend(struct.unpack_from(f"<{width}{fmt[0]}", binc, base + i * stride))
    return list(flat) if width == 1 else [tuple(flat[i:i + width]) for i in range(0, len(flat), width)]


def _node_matrix(node: dict) -> list:
    """The 4 x 4 row-major local matrix of a glTF node (``matrix`` or translation, rotation, scale)."""
    m = node.get("matrix")
    if isinstance(m, list) and len(m) == 16:
        return [[float(m[c * 4 + r]) for c in range(4)] for r in range(4)]
    t = [float(v) for v in (node.get("translation") or [0.0, 0.0, 0.0])]
    x, y, z, w = [float(v) for v in (node.get("rotation") or [0.0, 0.0, 0.0, 1.0])]
    s = [float(v) for v in (node.get("scale") or [1.0, 1.0, 1.0])]
    r = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
         [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
         [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    return [[r[i][0] * s[0], r[i][1] * s[1], r[i][2] * s[2], t[i]] for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]


def _mul(a: list, b: list) -> list:
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _identity() -> list:
    return [[1.0 if r == c else 0.0 for c in range(4)] for r in range(4)]


def _mesh_nodes(doc: dict) -> list[tuple[int, list]]:
    """``[(mesh index, world matrix)]`` of every node that draws a mesh (the default scene, else every root node)."""
    nodes = doc.get("nodes") or []
    scenes = doc.get("scenes") or []
    if scenes:
        roots = list((scenes[int(doc.get("scene") or 0)] if int(doc.get("scene") or 0) < len(scenes)
                      else scenes[0]).get("nodes") or [])
    else:
        children = {c for n in nodes for c in n.get("children") or []}
        roots = [i for i in range(len(nodes)) if i not in children]
    out, stack = [], [(root, _identity()) for root in roots]
    seen = set()
    while stack:
        i, parent = stack.pop()
        if not isinstance(i, int) or not 0 <= i < len(nodes) or i in seen:
            continue
        seen.add(i)
        world = _mul(parent, _node_matrix(nodes[i]))
        if isinstance(nodes[i].get("mesh"), int):
            out.append((nodes[i]["mesh"], world))
        stack.extend((c, world) for c in nodes[i].get("children") or [])
    if not out and not nodes:                                  # meshes without nodes: one each, unmoved
        out = [(k, _identity()) for k in range(len(doc.get("meshes") or []))]
    return out


def _textured_glass(m: dict) -> bool:
    """A glass material with an image on its colour (a patterned or frosted pane)."""
    if not _glass_material(m):
        return False
    pbr = m.get("pbrMetallicRoughness") or {}
    sg = (m.get("extensions") or {}).get("KHR_materials_pbrSpecularGlossiness") or {}
    return bool(pbr.get("baseColorTexture") or sg.get("diffuseTexture"))


def glb_panes(path) -> Optional[dict]:
    """The panes of a door or window model (pure; 26 Oct 2026, real06's "French Door": eight small lites per leaf
    under a dark lattice in a Scandinavian house): ``{"lites": n, "per_m2": n per square metre of the model's face,
    "patterned": a glass material carries an image, "glass_m2"}``. A lite is a connected piece of the glass triangles
    (vertices joined within 1 mm, so a pane's two faces are one piece), pieces whose outlines on the model's face
    overlap by half merged (a pane of two loose faces), pieces under ``MIN_LITE_M2`` left out. The face is the plane
    of the model's two longest sides (its depth is the shortest). None when the file cannot be read; ``lites`` None
    when its geometry cannot be read (only the materials are judged)."""
    parts = _glb_parts(path)
    if parts is None:
        return None
    doc, binc = parts
    mats = doc.get("materials") or []
    patterned = any(_textured_glass(m) for m in mats if isinstance(m, dict))
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    tris = []
    meshes = doc.get("meshes") or []
    for mi, world in _mesh_nodes(doc):
        if not 0 <= mi < len(meshes):
            continue
        for prim in meshes[mi].get("primitives") or []:
            if int(prim.get("mode", 4)) != 4:
                continue
            a = (prim.get("attributes") or {}).get("POSITION")
            m = prim.get("material")
            glassy = isinstance(m, int) and 0 <= m < len(mats) and _glass_material(mats[m])
            acc = (doc.get("accessors") or [])[a] if isinstance(a, int) and a < len(doc.get("accessors") or []) \
                else {}
            if not glassy and acc.get("min") and acc.get("max"):
                mn, mx = acc["min"][:3], acc["max"][:3]       # a frame part: the corners of its box are enough
                pos = [(x, y, z) for x in (mn[0], mx[0]) for y in (mn[1], mx[1]) for z in (mn[2], mx[2])]
            else:
                pos = _accessor(doc, binc, a)
            if not pos:
                continue
            pts = [tuple(world[r][0] * p[0] + world[r][1] * p[1] + world[r][2] * p[2] + world[r][3]
                         for r in range(3)) for p in pos]
            for p in pts:
                for k in range(3):
                    lo[k], hi[k] = min(lo[k], p[k]), max(hi[k], p[k])
            if not glassy:
                continue
            idx = _accessor(doc, binc, prim.get("indices")) if prim.get("indices") is not None \
                else list(range(len(pts)))
            if not idx:
                continue
            tris += [(pts[idx[i]], pts[idx[i + 1]], pts[idx[i + 2]]) for i in range(0, len(idx) - 2, 3)
                     if max(idx[i], idx[i + 1], idx[i + 2]) < len(pts)]
    if not math.isfinite(lo[0]):
        return {"lites": None, "per_m2": None, "patterned": patterned, "glass_m2": None}
    ext = [hi[k] - lo[k] for k in range(3)]
    depth = min(range(3), key=lambda k: ext[k])
    u, v = [k for k in range(3) if k != depth]
    face = ext[u] * ext[v]
    parent: dict = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def key(p):
        return tuple(int(round(c * 1000.0)) for c in p)

    for t in tris:
        ks = [key(p) for p in t]
        for k in ks[1:]:
            ra, rb = find(ks[0]), find(k)
            if ra != rb:
                parent[ra] = rb
    boxes: dict = {}
    for t in tris:
        root = find(key(t[0]))
        b = boxes.setdefault(root, [math.inf, math.inf, -math.inf, -math.inf])
        for p in t:
            b[0], b[1] = min(b[0], p[u]), min(b[1], p[v])
            b[2], b[3] = max(b[2], p[u]), max(b[3], p[v])
    pieces = list(boxes.values())
    merged = True
    while merged:                                   # a pane of two loose faces: one lite
        merged = False
        for i in range(len(pieces)):
            for j in range(i + 1, len(pieces)):
                a, b = pieces[i], pieces[j]
                w = min(a[2], b[2]) - max(a[0], b[0])
                h = min(a[3], b[3]) - max(a[1], b[1])
                small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
                if w > 0 and h > 0 and w * h >= 0.5 * small:
                    pieces[i] = [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]
                    del pieces[j]
                    merged = True
                    break
            if merged:
                break
    lites = [b for b in pieces if (b[2] - b[0]) * (b[3] - b[1]) >= MIN_LITE_M2]
    glass = sum((b[2] - b[0]) * (b[3] - b[1]) for b in lites)
    return {"lites": len(lites), "per_m2": round(len(lites) / face, 3) if face > 1e-9 else None,
            "patterned": patterned, "glass_m2": round(glass, 4)}


def _usable(entry: dict, mode: str) -> bool:
    from wenart.blender.site_models import MIN_VISION_QUALITY, vision_quality

    status = str(((entry.get("audit") or {}).get("status")) or "").lower()
    if status not in ("keep", "fix"):
        return False
    q = vision_quality(entry)
    if q is not None and q < MIN_VISION_QUALITY:
        return False
    flag = str(entry.get("licence_flag") or "unknown")
    if mode == "commercial":
        return flag == "none"
    return flag not in NEVER_FLAGS


def _title(entry: dict) -> str:
    return f" {str(entry.get('title') or entry.get('name') or '').lower()} "


def _has(title: str, words) -> bool:
    return any(f" {w}" in title or f"{w} " in title for w in words)


def model_size(entry: dict) -> Optional[tuple[float, float, float]]:
    """(width, depth, height) of a model in metres in its front frame: the catalogue box ``bbox_m``, which the
    catalogue writes in the piece frame already (``catalog.oriented_bbox``: the model box turned by its front axis;
    ``furniture.fit_vertices`` builds in that frame).

    27 Oct 2026 (user on real06's entrance: "correct the door"): this read swapped width and depth once more for a front
    along x, so a door whose audit put its front along the leaf ("Modern Single Door", front -X: the piece box 0.13 m
    wide and 1.07 m deep) passed as a 1.07 m leaf and was built turned 90 degrees, its 13 cm edge stretched to the
    opening's width (fit scale 6.1 x 0.1 x 0.9: a narrow oak strip beside a dark gap), while every door modelled with
    its face across x (front +X: "Front Door", "PVC Doors") was read 0.25 m wide and never used."""
    box = entry.get("bbox_m")
    if not box or len(box) < 3 or min(float(v) for v in box[:3]) <= 0.0:
        return None
    w, d, h = (float(v) for v in box[:3])
    return w, d, h


FRONT_TURN = {"-X": "-Y", "+X": "+Y", "-Y": "-X", "+Y": "+X"}


def leaf_front(entry: dict) -> dict:
    """A door or window model whose piece box is deeper than wide has its front along its leaf (an audit that read "a
    door has no front" and turned it, 27 Oct 2026): the front is turned 90 degrees (``FRONT_TURN``: the leaf's face
    becomes the front, the sign kept) and the box with it, noted ``front_axis_fixed``; any other entry is returned as
    it is (pure; a new dict when changed). A door or a window is always wider than its frame is deep."""
    box = entry.get("bbox_m")
    if entry.get("type") not in ("door", "window") or not box or len(box) < 3:
        return entry
    try:
        w, d, h = (float(v) for v in box[:3])
    except (TypeError, ValueError):
        return entry
    front = str(entry.get("front_axis") or "-Y").upper()
    if not (d > w > 0.0) or front not in FRONT_TURN:
        return entry
    out = dict(entry, front_axis=FRONT_TURN[front], bbox_m=[d, w, h] + list(box[3:]))
    out["front_axis_fixed"] = {"was": front, "box_was": list(box[:3]),
                               "reason": f"its piece box was {w:.2f} m wide and {d:.2f} m deep with the front {front}: "
                                         f"the front ran along the leaf; turned to {FRONT_TURN[front]} (the leaf's "
                                         f"face)"}
    return out


# 28 Oct 2026: how a model opens by its title (folding before sliding: "Folding Sliding Door" is a bi-fold) and how an
# opening opens by the architect's door kind, else its drawn operation
OPERATION_WORDS = (("folding", ("folding", "bifold", "bi-fold", "bi fold", "accordion")),
                   ("pivot", ("pivot",)),
                   ("hinged", ("french", "casement", "hinged")),
                   ("sliding", ("sliding", "slide", "lift-slide", "patio slider")))
KIND_OPERATION = {"glazed_sliding": "sliding", "sliding_pair": "sliding", "glazed_folding": "folding",
                  "folding": "folding", "french": "hinged", "double": "hinged", "entrance": "hinged"}


# 28 Oct 2026: the structured fields of a door or window model (the audit's opening question, the HSSD table)
MODEL_ROLES = ("entrance", "outside", "inside", "garage", "window")
GLASS_LEVELS = ("clear", "bars", "patterned")
DOOR_OPERATIONS = ("hinged", "sliding", "folding", "pivot")


def model_vision(entry: dict) -> dict:
    """The audit's opening answer of a model (``opening_vision``), {} without one."""
    v = entry.get("opening_vision") if isinstance(entry, dict) else None
    return v if isinstance(v, dict) else {}


def _opening_rec(entry: dict) -> dict:
    v = entry.get("opening") if isinstance(entry, dict) else None
    return v if isinstance(v, dict) else {}


def model_role(entry: dict) -> Optional[str]:
    """Where the audit puts a model (``MODEL_ROLES``), None when it does not say."""
    v = model_vision(entry).get("role")
    return v if v in MODEL_ROLES else None


def model_glazing(entry: dict) -> Optional[str]:
    """The audit's glass of a model: none, clear, bars, patterned; None when it does not say."""
    v = model_vision(entry).get("glazing")
    return v if v in ("none",) + GLASS_LEVELS else None


def model_leaves(entry: dict) -> Optional[int]:
    """The leaves of a door model side by side: the audit's count, else 2 for an HSSD ``double`` door; None unknown."""
    v = model_vision(entry).get("leaves")
    if isinstance(v, int) and not isinstance(v, bool) and v > 0:
        return v
    return 2 if _opening_rec(entry).get("kind") == "double" else None


def model_handle_side(entry: dict) -> Optional[str]:
    """Where the audit sees the handle in the model's front view: left, right, both, none; None unknown."""
    v = model_vision(entry).get("handle_side")
    return v if v in ("left", "right", "both", "none") else None


def model_glazed(entry: dict) -> bool:
    """Glass evidence without the file: the audit's glazing, a glass word of the title or the glass material tag."""
    g = model_glazing(entry)
    if g is not None:
        return g in GLASS_LEVELS
    return _has(_title(entry), ("glass", "glazed", "lite", "french")) or "glass" in (entry.get("material_tags") or [])


def model_operation(entry: dict) -> Optional[str]:
    """How a door model opens: the audit's operation (28 Oct 2026), else the HSSD table's, else its title
    (``OPERATION_WORDS``, the first that matches); None when nothing names one."""
    v = model_vision(entry).get("operation")
    if v in DOOR_OPERATIONS:
        return v
    op = _opening_rec(entry).get("operation")
    if op in DOOR_OPERATIONS:
        return op
    title = _title(entry)
    for op, words in OPERATION_WORDS:
        if _has(title, words):
            return op
    return None


def opening_operation(o: dict) -> Optional[str]:
    """How an opening opens: the architect's door kind (``KIND_OPERATION``), else its drawn ``operation`` (sliding,
    swing), None for a window or an unknown."""
    if o.get("type") != "door":
        return None
    kind = door_kind_of(o)
    if kind in KIND_OPERATION:
        return KIND_OPERATION[kind]
    op = str(o.get("operation") or "").lower()
    return {"sliding": "sliding", "swing": "hinged", "folding": "folding", "pivot": "pivot"}.get(op)


def operation_fit(cands: Sequence[dict], wanted: set) -> tuple[list[dict], dict]:
    """``(kept, {id: why})``: the models whose own operation (``model_operation``) is the one the openings want, or
    that name none; with several operations wanted only the models that name none (pure), and (28 Oct 2026) the
    models whose operation the audit or the HSSD table states and one of the openings wants (``plan`` gives each
    opening a member that opens its way: ``op_ok``)."""
    if not wanted:
        return list(cands), {}
    kept, wrong = [], {}
    for e in cands:
        op = model_operation(e)
        stated = model_vision(e).get("operation") in DOOR_OPERATIONS or \
            _opening_rec(e).get("operation") in DOOR_OPERATIONS
        if op is None or (op in wanted and (len(wanted) == 1 or stated)):
            kept.append(e)
        else:
            wrong[e.get("id")] = f"a {op} door for {', '.join(sorted(wanted))} opening(s)"
    return kept, wrong


def candidates(extras: Sequence[dict], category: str, mode: str) -> list[dict]:
    """The usable models of a category (see the module docstring), unranked. 29 Oct 2026: never a model the build
    would refuse to load (``build_refusal``): the plan and the build read one record."""
    kind = "window" if category == "window" else "door"
    (w0, w1), (h0, h1) = SIZES[category]
    out = []
    for e in extras:
        if e.get("type") != kind or not _usable(e, mode) or not e.get("glb") or build_refusal(e):
            continue
        size = model_size(e)
        if size is None:
            continue
        w, d, h = size
        title = _title(e)
        if not (w0 <= w <= w1 and h0 <= h <= h1 and d <= MAX_DEPTH_M) or _has(title, NOT_WORDS[category]):
            continue
        if category in ("glazed_door", "terrace_door") and not (_has(title, WORDS[category])
                                                                or "glass" in (e.get("material_tags") or [])
                                                                or model_glazing(e) in GLASS_LEVELS):
            continue
        if structured_problem(e, category):
            continue
        out.append(e)
    return out


FACADE_CATEGORIES = ("entrance", "door", "glazed_door", "terrace_door")
INSIDE_CATEGORY = "inside_door"


def structured_problem(e: dict, category: str) -> Optional[str]:
    """Why a model's structured fields (the audit, the HSSD table) rule it out of a category (pure, 28 Oct 2026),
    None when they do not: an inside door, a garage door or a window never on the facade; an entrance, outside or
    garage door never inside; a pair never in a one-leaf category; a door without glass never a glazed door."""
    role = model_role(e)
    if category in FACADE_CATEGORIES and role in ("inside", "garage", "window"):
        return f"the audit puts it {'inside' if role == 'inside' else 'as a ' + role}: not a {category}"
    if category == INSIDE_CATEGORY and role in ("entrance", "outside", "garage", "window"):
        return f"the audit puts it {'outside' if role == 'outside' else 'as a ' + role}: no inside door"
    if category == "window" and role in ("entrance", "outside", "inside", "garage"):
        return f"the audit sees a door ({role}): no window"
    if category in SINGLE_LEAF + (INSIDE_CATEGORY,) and (model_leaves(e) or 1) >= 2:
        return f"{model_leaves(e)} leaves: no one-leaf door"
    if category in ("glazed_door", "terrace_door") and model_glazing(e) == "none":
        return "no glass (the audit): no glazed door"
    return None


def best_panels(width: float, height: float, model_aspect: float) -> tuple[int, float]:
    """``(panels, error)``: how many panels side by side give the opening's panels the model's proportions best, and
    the remaining log error."""
    if width <= 0 or height <= 0 or model_aspect <= 0:
        return 1, math.inf
    best = (1, math.inf)
    for n in range(1, MAX_PANELS + 1):
        err = abs(math.log((width / n / height) / model_aspect))
        if err < best[1] - 1e-9:
            best = (n, err)
    return best


def _rank_key(entry: dict, category: str, openings: Sequence[tuple[float, float]]):
    w, _d, h = model_size(entry)
    errs = [best_panels(ow, oh, w / h)[1] for ow, oh in openings] or [0.0]
    title = _title(entry)
    status = str((entry.get("audit") or {}).get("status") or "").lower()
    # 28 Oct 2026: the audit's vision quality first (a 4 before a 3; unknown counts as 3), then the audit's role (a
    # model the audit puts where the category is before an unknown one), then as before
    return (-_quality(entry), role_rank(entry, category), 0 if entry.get("textured") else 1,
            0 if _has(title, WORDS[category]) else 1, 0 if status == "keep" else 1,
            RANK_STEP * round(sum(min(e, 1.0) for e in errs) / len(errs) / RANK_STEP), str(entry.get("id")))


def _quality(entry: dict) -> int:
    """The audit's vision quality of a model (``audit_quality``), 3 when unknown."""
    q = entry.get("audit_quality")
    return q if isinstance(q, int) and not isinstance(q, bool) else 3


CATEGORY_ROLES = {"entrance": ("entrance",), "door": ("outside", "entrance"), "glazed_door": ("outside",),
                  "terrace_door": ("outside",), "window": ("window",), "inside_door": ("inside",)}


def role_rank(entry: dict, category: str) -> int:
    """0: the audit puts the model where the category is (``CATEGORY_ROLES``), 1: it does not say, 2: elsewhere."""
    role = model_role(entry)
    if role is None:
        return 1
    return 0 if role in CATEGORY_ROLES.get(category, ()) else 2


def is_statement(entry: dict) -> bool:
    """A statement front door (28 Oct 2026): the audit puts it at the entrance, or its title names a front door."""
    return model_role(entry) == "entrance" or _has(_title(entry), WORDS["entrance"])


def house_seed(building: dict) -> Optional[str]:
    """The house's variation seed: its project id (``building.project.id``), else its name; None without one."""
    proj = (building or {}).get("project")
    if isinstance(proj, dict):
        proj = proj.get("id") or proj.get("name")
    return str(proj) if proj else None


def _choose_family(cands: Sequence[dict], category: str, openings: Sequence[tuple[float, float]], look_rank: dict,
                   seed: Optional[str] = None, exclude=(), prefer: Optional[str] = None,
                   statement: bool = False, ops: Optional[Sequence] = None) -> Optional[tuple]:
    """``(order, key, members, tier)`` of the family a category takes (pure; module docstring): the families of the
    ranked candidates (``family_key``) that fit an opening, ordered by the look, the ``prefer`` family (the glazed
    inside doors: the solid ones' series), the audit's quality, a statement door (``statement``: the entrance), the
    openings covered and ``_rank_key``; ``exclude`` families are left out (the entrance's, the facade's). Among the
    families equal on all of these (the ``tier``) the house's ``seed`` picks one (28 Oct 2026: two houses of one
    style get different products); without a seed the first. ``ops`` (one per opening): the way each opening
    opens; a member covers an opening only when it opens that way or says nothing (``op_ok``). None when no family
    fits."""
    ranked = sorted(cands, key=lambda e: (look_rank[e["id"]][0], _rank_key(e, category, openings)))
    families: dict[str, list] = {}
    for e in ranked:
        families.setdefault(family_key(e), []).append(e)
    rows = []
    for key, members in families.items():
        if key in exclude:
            continue
        ways = list(ops) if ops is not None else [None] * len(openings)
        covered = sum(1 for (w, h), op in zip(openings, ways)
                      if any(op_ok(m, op) and fit(m, category, w, h) for m in members))
        if not covered:
            continue
        head = members[0]
        quality = max(_quality(m) for m in members)
        stmt = 0 if not statement or any(is_statement(m) for m in members) else 1
        pref = 0 if prefer is None or key == prefer else 1
        rows.append(((look_rank[head["id"]][0], pref, -quality, stmt, -covered, _rank_key(head, category, openings)),
                     key, members))
    if not rows:
        return None
    rows.sort(key=lambda r: r[0])
    best = rows[0][0]
    tier = [r for r in rows if r[0][:5] == best[:5] and r[0][5][:-1] == best[5][:-1]]
    pick = rows[0]
    if seed and len(tier) > 1:
        pick = tier[int(hashlib.sha256(f"{seed}|{category}".encode("utf-8")).hexdigest(), 16) % len(tier)]
    return pick[0], pick[1], pick[2], len(tier)


def op_ok(model: dict, wanted: Optional[str]) -> bool:
    """A model serves an opening that opens ``wanted``: it opens that way or names no way (28 Oct 2026)."""
    op = model_operation(model)
    return wanted is None or op is None or op == wanted


def _number(v) -> Optional[float]:
    if isinstance(v, dict):
        v = v.get("value")
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


ASSET_KEYS = ("id", "glb", "front_axis", "up_axis", "unit_scale", "origin_offset", "bbox_m", "source", "licence",
              "licence_url", "licence_flag", "licence_declared_by", "commercial_safe", "uid", "front_axis_fixed",
              "series")
# 29 Oct 2026 (user: "Better door models needed"; real06 run 20261028-154514-full): = furniture.CC_BY_FIELDS, the
# credit line a CC BY licence (and its NC / SA variants) asks for; the build refuses an asset without it
CREDIT_FIELDS = ("title", "author", "source_url", "licence_url", "via", "attribution")


def asset_of(entry: dict) -> dict:
    """The fields the build needs to load and frame a model (``furniture.resolve_asset`` / ``fit_vertices``) and the
    report needs to credit it.

    29 Oct 2026 (user: "Better door models needed"; real06 run 20261028-154514-full: 15 of its 23 door objects were
    the parametric door): the record carries every credit field (``CREDIT_FIELDS``). It left out ``source_url`` and
    ``via``, so ``furniture.licence_refusal`` refused every HSSD door and window at the build ("CC BY 4.0 without
    source_url, via (no credit line); refused") and the build made the parametric opening instead: the 197 audited HSSD
    doors and windows adopted on 28 Oct never reached a render (real04: the entrance, 4 inside doors, 10 windows)."""
    keys = ASSET_KEYS + tuple(k for k in CREDIT_FIELDS if k not in ASSET_KEYS)
    out = {k: entry.get(k) for k in keys if entry.get(k) is not None}
    out.update(method="library", asset_id=entry.get("id"), library=entry.get("source") or "3dwh")
    return out


def build_refusal(entry: dict) -> Optional[str]:
    """Why the build would refuse to load a catalogue model (``furniture.licence_refusal`` on ``asset_of``: its
    licence and credit line), None when it may (pure; 29 Oct 2026). An entry without a catalogue licence (a test
    fixture) is not judged: the catalogue writes one for every entry (``catalog.CC_BY_FIELDS``)."""
    if not str(entry.get("licence") or entry.get("license") or "").strip():
        return None
    from wenart.blender.furniture import licence_refusal
    return licence_refusal(asset_of(entry))


# 26 Oct 2026 (architect D5, ``architect_actions.DOOR_KINDS``): the door kinds no library category holds (a sectional
# garage door, a pair or a row of solid leaves: the categories' doors are one solid leaf or glass): the parametric door
NO_LIBRARY_KINDS = ("garage_sectional", "double", "sliding_pair", "folding")
GLAZED_KINDS = ("french", "glazed_sliding", "glazed_folding")


def door_kind_of(o: dict) -> Optional[str]:
    """The kind the architect gave a door (D5: ``door_type``, else ``door_decision.kind``), None without one."""
    dec = o.get("door_decision") if isinstance(o.get("door_decision"), dict) else {}
    return o.get("door_type") or dec.get("kind")


def is_glazed_door(o: dict) -> bool:
    """A door the architect made glazed (D5's glazed kinds, or ``glazed``: a gap made a glazed door)."""
    return o.get("type") == "door" and (bool(o.get("glazed")) or door_kind_of(o) in GLAZED_KINDS)


def categorise(building: dict, outer: Sequence[dict]) -> dict[str, str]:
    """``{opening id: category}`` of the outer openings (``site.outer_openings`` records). 26 Oct 2026 (architect
    D5): a door's decided kind first: a glazed door is a ``glazed_door`` (``WIDE_DOOR_M`` or wider) or a
    ``terrace_door``; a sectional garage door or a pair of solid leaves has no category (the parametric door); the
    main entrance is an ``entrance`` when its kind is ``entrance`` or it has none (real06: a 2.95 m drawn sliding door
    was the main entrance record, was matched against single front doors, none fitted, and the parametric builder
    made one flat leaf as wide as the opening; D5 makes it a glazed sliding door)."""
    entrances = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
                 and not r.get("into_air") and not r.get("below_ground")]
    main = next((r.get("door_id") for r in entrances if r.get("main")), None)
    if main is None and entrances:
        main = entrances[0].get("door_id")
    out = {}
    for rec in outer:
        o = rec["opening"]
        width = _number(o.get("width")) or 0.0
        kind = door_kind_of(o) if o.get("type") == "door" else None
        if kind in NO_LIBRARY_KINDS:
            continue
        if is_glazed_door(o):
            out[o["id"]] = "glazed_door" if width >= WIDE_DOOR_M else "terrace_door"
        elif o.get("type") == "door" and o.get("outside_door") and o["id"] != main:
            # 25 Oct 2026 (architect A3): a door to a terrace or balcony room is a glazed outside door
            out[o["id"]] = "glazed_door" if width >= WIDE_DOOR_M else "terrace_door"
        elif o.get("type") == "door":
            entrance = kind == "entrance" or (o["id"] == main and kind is None)
            out[o["id"]] = "entrance" if entrance else ("glazed_door" if width >= WIDE_DOOR_M else "door")
        elif o.get("type") == "window":
            out[o["id"]] = "window"
    return out


SINGLE_LEAF = ("entrance", "door", "terrace_door")       # one panel: the model is one door
CATEGORIES = ("entrance", "door", "glazed_door", "terrace_door", "window")
SINGLE_LEAF_MAX_M = 1.25           # = parametric.SINGLE_LEAF_MAX_M: no one-leaf model is stretched wider (27 Oct 2026)


def fit(entry: dict, category: str, width: float, height: float) -> Optional[tuple[int, float]]:
    """``(panels, log proportion error)`` of a model in an opening ``width`` x ``height`` (pure), None when it does
    not fit: the error over ``ASPECT_TOL`` or the height beyond ``MAX_SCALE`` of the model's. 27 Oct 2026 (user on
    real06's entrance: "correct the door"): a one-leaf model fills its opening as a real door does, so an opening wider
    than ``SINGLE_LEAF_MAX_M`` takes no one-leaf model (the parametric door: the entrance's leaf with glazed side
    lights, D5's pair or glazed door), never one leaf stretched past a real leaf's width."""
    size = model_size(entry)
    if size is None or width <= 0 or height <= 0:
        return None
    w, _d, h = size
    if category in SINGLE_LEAF or category == INSIDE_CATEGORY:
        if width > SINGLE_LEAF_MAX_M + 1e-6:
            return None
        n, err = 1, abs(math.log((width / height) / (w / h)))
    else:
        n, err = best_panels(width, height, w / h)
    if err <= ASPECT_TOL and abs(math.log(height / h)) <= math.log(MAX_SCALE):
        return n, err
    return None


def _checked(cands: list, category: str, look: Optional[dict], assets_dir, cache: dict
             ) -> tuple[list, dict, dict]:
    """``(kept, left out {id: why}, look rank {id: rank})`` of a category's candidates: see-through glass and the
    glass share with the files (25 Oct 2026), then the house's look (``look_fit``; the panes with the files)."""
    kept, left, rank = [], {}, {}

    def cached(what, fn, path):
        if (what, str(path)) not in cache:
            cache[(what, str(path))] = fn(path)
        return cache[(what, str(path))]

    for e in cands:
        path = Path(assets_dir) / str(e.get("glb") or "") if assets_dir is not None else None
        if path is not None and category in GLAZED:
            if cached("glass", glb_glass, path) is False:
                left[e["id"]] = "no see-through glass"
                continue
        if path is not None and category in ("glazed_door", "terrace_door"):
            # a door to a terrace is mostly glass (a wood door with small panes is an inside or a front door)
            share = cached("share", glb_glass_share, path)
            if share is not None and share < GLAZED_DOOR_MIN_SHARE:
                left[e["id"]] = f"glass {share:.0%} of its face (< {GLAZED_DOOR_MIN_SHARE:.0%})"
                continue
        panes = None
        if path is not None and look is not None:
            panes = cached("panes", glb_panes, path)
        r, why = look_fit(e, look, panes, category)
        if r is None:
            left[e["id"]] = why
            continue
        kept.append(e)
        rank[e["id"]] = (r, why)
    return kept, left, rank




def _entry(e: dict, category: str, n: int, err: float, width: float, height: float, key: str, look: Optional[dict],
           look_rank: dict, outward, what: str) -> dict:
    """The plan entry of one opening's model (``plan`` / ``plan_inside``)."""
    rank, why = look_rank[e["id"]]
    styled = f"; {look['family']} look: {why}" if look is not None else ""
    return {"asset": asset_of(e), "panels": n, "category": category, "aspect_error": round(err, 4),
            "outward": outward, "family": key,
            "look": None if look is None else {"family": look["family"], "name": look["name"], "rank": rank,
                                               "styles": entry_styles(e)},
            "quality": _quality(e), "model_role": model_role(e), "model_operation": model_operation(e),
            # 29 Oct 2026: the leaf the audit's opening question saw (None: never asked; Argus U18 reads it)
            "leaf": model_vision(e).get("leaf"),
            "reason": f"library {category.replace('_', ' ')} {e.get('id')} ({str(e.get('title') or '')[:40]!r}) in "
                      f"{n} panel(s) of {width / n:.2f} x {height:.2f} m (proportions off by "
                      f"{(math.exp(err) - 1) * 100:.0f} %; the documents draw the opening, not its product); {what}"
                      f"{styled}; frames in the style's finish"}


def plan(building: dict, outer: Sequence[dict], extras: Sequence[dict], mode: str = "relaxed",
         assets_dir=None, style=None, notes: Optional[list] = None, seed=None) -> dict[str, dict]:
    """``{opening id: {"asset", "panels", "category", "aspect_error", "family", "look", "reason"}}`` for the outer
    openings ``outer`` (``site.outer_openings`` records: ``opening``, ``bottom``, ``top``). With ``assets_dir`` a
    window or glazed door model must have see-through glass (``glb_glass``; a model whose file is not there is not
    judged) and its panes are judged (``glb_panes``).

    26 Oct 2026: ``style`` (the style profile or its family name) picks the look (``look_of``, ``look_fit``); every
    category takes one model family (``family_key``): the family whose best model ranks first by look, then covers
    the most of the category's openings, then by ``_rank_key``; each opening takes the family's member that fits it
    best, and an opening no member fits keeps the parametric opening in the style's finish. ``notes`` (a list) gets
    ``{"kind": "left_out", "category", "models": {id: why}}`` per category and ``{"kind": "parametric", "id",
    "category", "reason"}`` per opening left to the parametric build.

    28 Oct 2026 (module docstring): the family choice is ``_choose_family`` (the entrance a statement door; the
    outside service doors never the entrance's family; the house's ``seed``, default ``house_seed(building)``,
    picks among equal families; ``seed=""`` turns that off); each opening takes a member that opens its way
    (``op_ok``)."""
    look = look_of(style)
    cats = categorise(building, outer)
    seed = house_seed(building) if seed is None else (seed or None)
    # 26 Oct 2026 (architect D5): a glazed door narrower than WIDE_DOOR_M tries the house's glazed door family first,
    # so the glazed doors share one look where a model fits within its stretch caps; else its terrace door
    narrow_glazed = [rec["opening"]["id"] for rec in outer if is_glazed_door(rec["opening"])
                     and cats.get(rec["opening"]["id"]) == "terrace_door"]
    sizes: dict[str, tuple[float, float]] = {}
    outward = {rec["opening"]["id"]: [round(float(v), 6) for v in rec["outward"][:2]] for rec in outer
               if rec.get("outward") is not None}
    for rec in outer:
        o = rec["opening"]
        width = _number(o.get("width")) or 0.0
        height = float(rec["top"]) - float(rec["bottom"])
        if width > 0 and height > 0:
            sizes[o["id"]] = (width, height)
    out: dict[str, dict] = {}
    cache: dict = {}
    by_id = {rec["opening"]["id"]: rec["opening"] for rec in outer}
    notes = notes if notes is not None else []
    chosen: dict[str, set] = {}                            # category -> the families it took
    for category in CATEGORIES:
        ids = [i for i, c in cats.items() if c == category and i in sizes and i not in out]
        also = [i for i in narrow_glazed if i in sizes and i not in out] if category == "glazed_door" else []
        if not ids and not also:
            continue
        base, left, look_rank = _checked(candidates(extras, category, mode), category, look, assets_dir, cache)
        # 28 Oct 2026 (user on real06: "This window / door should have been sliding as indicated in the plan": the
        # drawn 2.95 m sliding door got "Valdi - Folding Sliding Door"): a model that names how it opens opens as the
        # openings do; a category whose openings open two ways takes a family for each way
        ops = {i: opening_operation(by_id[i]) for i in ids + also if i in by_id}
        cands, wrong = operation_fit(base, set(v for v in ops.values() if v))
        if wrong:
            left = dict(left or {}, **wrong)
        if left:
            notes.append({"kind": "left_out", "category": category, "models": left})
        if not cands:
            continue
        # 28 Oct 2026 (user: "some variation is needed"): the outside service doors are not the entrance's family;
        # 29 Oct 2026 (real04: the entrance and both terrace doors one HSSD series): nor the glazed and terrace doors
        exclude = set(chosen.get("entrance") or ()) if category in SERVICE_DOORS else set()
        group = ids + also
        openings = [sizes[i] for i in group]
        pick = _choose_family(cands, category, openings, look_rank, seed, exclude, statement=category == "entrance",
                              ops=[ops.get(i) for i in group])
        if exclude:
            # another family than the entrance's only when one of the same look exists (an off-look model would be
            # worse than the entrance's family: one language before variety)
            shared = _choose_family(cands, category, openings, look_rank, seed, (), ops=[ops.get(i) for i in group])
            # 29 Oct 2026: by the look of the styles (``_look_rank``): a leaf the audit never saw (``look_fit``'s
            # leaf rule) orders the families, it does not make a model off the look
            if shared is not None and (pick is None or _look_rank(pick[2][0], look, None, category)[0]
                                       > _look_rank(shared[2][0], look, None, category)[0]):
                pick, exclude = shared, set()
                notes.append({"kind": "shared_family", "category": category, "family": shared[1],
                              "reason": "no other family of the house's look fits the outside service doors: they "
                                        "share the entrance's family"})
        if pick is None:
            for oid in ids:
                notes.append({"kind": "parametric", "id": oid, "category": category,
                              "reason": f"no library {category.replace('_', ' ')} fits {sizes[oid][0]:.2f} x "
                                        f"{sizes[oid][1]:.2f} m: the parametric opening in the style's finish"})
            continue
        _order, key, members, tier = pick
        chosen.setdefault(category, set()).add(key)
        what = (f"the building's one {category.replace('_', ' ')} family"
                + (f" (one of {tier} equal families, picked by the house's seed)" if tier > 1 and seed else "")
                + ("; another family than the entrance's" if exclude else ""))
        missing = _place(group, members, key, category, sizes, ops, look, look_rank, outward, what, out)
        # 29 Oct 2026 (real06's 1.98 m hinged glazed door stayed parametric: the glazed door family was a sliding
        # series): the openings whose way no member of the family opens take a second family of the house's look
        # that opens their way
        way = [oid for oid in missing if ops.get(oid) and not any(op_ok(m, ops[oid]) for m in members)]
        second = _choose_family(cands, category, [sizes[i] for i in way], look_rank, seed, exclude | {key},
                                ops=[ops[i] for i in way]) if way else None
        if second is not None and second[0][0] <= pick[0][0]:
            chosen[category].add(second[1])
            what2 = (f"the building's {category.replace('_', ' ')} family for the doors that open "
                     f"{'/'.join(sorted({ops[i] for i in way}))} (the first, {key}, opens another way)")
            served = set(way) - set(_place(way, second[2], second[1], category, sizes, ops, look, look_rank, outward,
                                           what2, out))
            missing = [oid for oid in missing if oid not in served]
        for oid in missing:
            if oid in also:
                continue                         # no member of the glazed door family fits: its terrace door next
            width, height = sizes[oid]
            head = members[0]
            notes.append({"kind": "parametric", "id": oid, "category": category, "family": key,
                          "reason": f"no model of the building's {category.replace('_', ' ')} family "
                                    f"{str(head.get('title') or head.get('id'))[:40]!r} fits {width:.2f} x "
                                    f"{height:.2f} m (or opens {ops.get(oid) or 'its'} way): the parametric "
                                    f"opening in the style's finish keeps one door and window language"})
    return out


SERVICE_DOORS = ("door", "glazed_door", "terrace_door")     # 29 Oct 2026: never the entrance's family when one fits


def _place(group, members, key, category, sizes, ops, look, look_rank, outward, what, out) -> list:
    """Each opening of ``group`` takes the family member that fits it best and opens its way (``plan``; in place in
    ``out``); returns the openings no member serves. 29 Oct 2026: a hinged door built of two or more panels of a
    one-leaf model is a pair (``pair``: the build mirrors the leaves so they meet in the middle)."""
    missing = []
    for oid in group:
        width, height = sizes[oid]
        fits = [(look_rank[m["id"]][0], f[1], i, m, f) for i, m in enumerate(members) if op_ok(m, ops.get(oid))
                for f in [fit(m, category, width, height)] if f is not None]
        if not fits:
            missing.append(oid)
            continue
        _r, err, _i, e, (n, err) = min(fits, key=lambda t: t[:3])
        out[oid] = _entry(e, category, n, err, width, height, key, look, look_rank, outward.get(oid), what)
        if category == "entrance":
            out[oid]["statement"] = is_statement(e)
        if category != "window" and n >= PAIR_LEAVES and (model_leaves(e) or 1) == 1 \
                and ops.get(oid) in (None, "hinged") and model_operation(e) in (None, "hinged"):
            out[oid].update(pair=True, handle_side=model_handle_side(e))
    return missing


# --------------------------------------------------------------------------
# Inside doors (28 Oct 2026)
# --------------------------------------------------------------------------

INSIDE_ROLES = ("solid", "glazed", "sliding")
# the door style of looks.door_look -> the inside door role; the others (pocket, double, folding, fixed, entrance,
# glazed sliding, sectional) stay the parametric door: no library model of that kind
ROLE_STYLES = {"flush": "solid", "shaker_panel": "solid", "glazed": "glazed", "sliding": "sliding",
               "barn": "sliding"}
INSIDE_GLAZED_MIN_SHARE = 0.15     # a glazed inside door is at least this much glass (a framed glass panel)
INSIDE_SOLID_MAX_SHARE = 0.08      # a solid one at most this much (a vision strip)
BARN_FAMILIES = ("rustic", "industrial")
# 29 Oct 2026 (real04 run 20261028-183611-full: a "bathroom door" with a vent grille on every bedroom and hall door):
# the title word of a door made for one kind of room -> the room types (``wenart.building.ROOM_TYPES``) it serves
ROOM_NAMED = (("bathroom", ("bathroom", "wc")), ("toilet", ("bathroom", "wc")), ("wc ", ("bathroom", "wc")),
              ("shower", ("bathroom",)), ("bedroom", ("bedroom",)), ("closet", ("storage",)),
              ("wardrobe", ("storage",)), ("pantry", ("storage", "kitchen")), ("cellar", ("storage",)),
              ("laundry", ("storage", "laundry")), ("kitchen", ("kitchen",)))
PAIR_LEAVES = 2                    # a pair of leaves (D5's double): two leaves of the role's model, the second mirrored


def model_rooms(entry: dict) -> set:
    """The room types a door model is made for by its title (``ROOM_NAMED``: "bathroom door" -> bathroom, wc); an
    empty set for a door of any room (pure, 29 Oct 2026)."""
    title = _title(entry)
    out: set = set()
    for word, types in ROOM_NAMED:
        if _word(title, (word,)):
            out |= set(types)
    return out


def is_pair(o: dict) -> bool:
    """A swing door of two leaves (the architect's ``double``, or two drawn leaves of a swing door): two leaves of one
    model, the second mirrored, can build it (29 Oct 2026); a sliding pair, a folding or a garage door cannot."""
    kind = door_kind_of(o)
    leaves = o.get("leaves")
    two = isinstance(leaves, int) and not isinstance(leaves, bool) and leaves == PAIR_LEAVES
    op = str(o.get("operation") or "swing").lower()
    return kind == "double" or (kind is None and two and op in ("swing", "double"))
# = architect.OPEN_AIR_TYPES: a door to one of these rooms is an outside door, never an inside door model
OPEN_AIR_TYPES = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch", "garden")


def _sides(centre, wall: dict, rooms: Sequence[dict]) -> list:
    """The rooms on the two sides of a wall at ``centre`` (left of the wall direction first; None: no room)."""
    from wenart import geometry as G
    from wenart.blender import shell as SH
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + SH.DEFAULTS["face_probe"]
    out = []
    for side in (1, -1):
        probe = (centre[0] + side * nx * reach, centre[1] + side * ny * reach)
        out.append(next((r for r in rooms if len(r.get("polygon") or []) >= 3
                         and G.point_in_polygon(probe, r["polygon"])), None))
    return out


def inside_records(building: dict, levels: Sequence[dict], skip=()) -> list[dict]:
    """The interior doors of ``levels`` (pure): ``[{"opening", "level", "centre", "joins", "rooms", "outward",
    "swing_room", "swing_assumed", "bottom", "top", "thickness"}]`` for every door with a room on both sides of its
    wall (``skip``: the ids the facade plan holds; virtual separators and ``outside_door`` doors left out).
    ``outward`` is the plan direction into the room the door opens into (``shell.opening_room_side``: its
    ``swing_side``, else the only room, else the wall's right side, assumed); the model's front faces it."""
    from wenart import geometry as G
    from wenart.blender import shell as SH
    ids = {lv["id"]: lv for lv in levels}
    every = list(building.get("levels") or levels)
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") in ids}
    skip = set(skip or ())
    out = []
    for o in building.get("openings") or []:
        lv = ids.get(o.get("level_id"))
        wall = walls.get(o.get("wall_id"))
        if o.get("type") != "door" or lv is None or wall is None or o.get("id") in skip or SH.is_virtual(o) \
                or o.get("outside_door") or not _number(o.get("width")):
            continue
        rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lv["id"]]
        cx, cy, _shift = SH.opening_centre_on_wall(o, wall)
        both = _sides((cx, cy), wall, rooms)
        if None in both or any(str(r.get("room_type") or "").lower() in OPEN_AIR_TYPES for r in both):
            continue                                     # outside (or open air) on one side: an outside door
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in every)
        bottom, top, _assumed = SH.opening_vertical(o, lv, above)
        side, room, assumed = SH.opening_room_side((cx, cy), wall, rooms, o.get("swing_side"))
        nx, ny = G.unit_normal_left(wall["start"], wall["end"])
        out.append({"opening": o, "level": lv, "centre": (cx, cy), "rooms": [r.get("id") for r in both],
                    "joins": [r.get("room_type") for r in both], "outward": [round(side * nx, 6), round(side * ny, 6)],
                    "swing_room": room, "swing_assumed": assumed, "bottom": bottom, "top": top,
                    "thickness": float(wall["thickness"])})
    return out


def inside_role(rec: dict, style=None) -> tuple[Optional[str], str]:
    """``(role, why)`` of an interior door (``INSIDE_ROLES``), or ``(None, why)``: the door style ``looks.door_look``
    gives it (the drawn operation first, then the style's door style, then the rooms it joins:
    ``looks.role_door_style``), so the library model and the parametric door agree (``ROLE_STYLES``); a pocket,
    folding or fixed door stays parametric.

    29 Oct 2026 (user: "Better door models needed"; real06's 1.95 m double door between the living room and the
    kitchen was the parametric pair): a pair (``is_pair``) takes the role of the rooms it joins (glazed into the living
    rooms or when the architect glazed it, else solid); ``plan_inside`` builds it of two leaves of the role's model."""
    from wenart.blender import looks as LK
    o = rec["opening"]
    kind = door_kind_of(o)
    leaves = o.get("leaves")
    prof = style if isinstance(style, dict) else ({"family": style} if style else {})
    lite = LK.divided_lite(dict(o, joins=rec.get("joins")), prof, o.get("door_style") or "double")
    if lite is not None and lite["door_style"] == "glazed_sliding":
        # 29 Oct 2026 (D3): a wide sliding door between day rooms is the parametric glazed divided-lite sliding door
        # (a swing pair keeps its library leaves; the parametric pair, where none fits, is the divided-lite pair)
        return None, lite["why"] + ": the parametric door (no library model of that kind)"
    if is_pair(o):
        rs, why = LK.role_door_style(rec.get("joins"), prof)
        role = "glazed" if (o.get("glazed") or rs == "glazed") else "solid"
        return role, (f"a pair of leaves: two {role} leaves of the house's {role} inside door, the second mirrored"
                      + (f" ({why})" if why else ""))
    if kind in NO_LIBRARY_KINDS or (isinstance(leaves, int) and not isinstance(leaves, bool) and leaves >= 2):
        return None, f"a {kind or 'pair of leaves'}: the parametric door (no one-leaf model)"
    dl = LK.door_look(prof, dict(o, joins=rec.get("joins")))
    ds = dl.get("door_style")
    role = ROLE_STYLES.get(ds)
    if role is None:
        return None, f"door style {ds}: no library model of that kind (the parametric door)"
    return role, f"door style {ds}: {dl.get('reason')}"


def _inside_problem(e: dict, role: str, family: Optional[str], assets_dir, cache: dict) -> Optional[str]:
    """Why a model does not serve an inside door role (pure apart from the cached file reads), None when it does."""
    op = model_operation(e)
    path = Path(assets_dir) / str(e.get("glb") or "") if assets_dir is not None else None

    def share():
        if path is None:
            return None
        key = ("share", str(path))
        if key not in cache:
            cache[key] = glb_glass_share(path)
        return cache[key]
    if role == "sliding":
        if op != "sliding":
            return f"a {op or 'swing'} door for a drawn sliding door"
        barn = _has(_title(e), ("barn",)) or model_vision(e).get("leaf") == "plank"
        if barn and family not in BARN_FAMILIES:
            return f"a barn door: not the {family or 'house'} style (rustic and industrial only)"
        return None
    if op in ("sliding", "folding"):
        return f"a {op} door for a swing door"
    g = model_glazing(e)
    sh = share()
    if role == "glazed":
        if g == "none":
            return "no glass (the audit): a solid leaf"
        if sh is not None and sh < INSIDE_GLAZED_MIN_SHARE:
            return f"glass {sh:.0%} of its face (< {INSIDE_GLAZED_MIN_SHARE:.0%}): not a glazed leaf"
        if sh is None and not model_glazed(e):
            return "no glass known (the audit, the title, the materials): not a glazed leaf"
        return None
    if g in GLASS_LEVELS:
        return f"glazed (the audit: {g} glass): not a solid leaf"
    if sh is not None and sh > INSIDE_SOLID_MAX_SHARE:
        return f"glass {sh:.0%} of its face (> {INSIDE_SOLID_MAX_SHARE:.0%}): not a solid leaf"
    if sh is None and model_glazed(e):
        return "glazed by its title or materials: not a solid leaf"
    return None


def hinge_mirror(o: dict, model: dict) -> tuple[bool, str]:
    """``(mirror, why)`` of an inside door model (28 Oct 2026): the drawing's ``hinge_side`` (left / right, seen from
    the room the door opens into, where the model's front faces) against the model's handle in its front view (the
    audit's ``handle_side``); mirrored when they do not agree; kept as modelled (assumed) when either is unknown."""
    drawn = str(o.get("hinge_side") or "").strip().lower()
    hs = model_handle_side(model)
    chosen = ""
    if drawn not in ("left", "right"):
        # 29 Oct 2026 (D1, UL116): the hinge side door_states chose so the open leaf stands by the wall beside it
        chosen = str((o.get("leaf_state") or {}).get("hinge_side") or "").strip().lower()
        if chosen in ("left", "right") and (o.get("leaf_state") or {}).get("state") in ("open", "ajar"):
            drawn = chosen
    if drawn not in ("left", "right"):
        return False, "the drawing gives no hinge side: the model's own hinge side (assumed)"
    if hs not in ("left", "right"):
        return False, f"the model's handle side is not known ({hs or 'no audit answer'}): kept as modelled (assumed)"
    want = "right" if drawn == "left" else "left"
    if hs == want:
        return False, f"its handle on the {hs}: hinged on the drawn {drawn}"
    return True, f"mirrored: its handle was on the {hs}, the drawing hinges the door on the {drawn}"


def plan_inside(building: dict, inside: Sequence[dict], extras: Sequence[dict], mode: str = "relaxed",
                assets_dir=None, style=None, notes: Optional[list] = None, exclude_families=(),
                seed=None) -> dict[str, dict]:
    """``{opening id: entry}`` of library models for the interior doors ``inside`` (``inside_records``; module
    docstring): category ``inside_door``, one family per role (``inside_role``: solid first, then glazed, which
    prefers the solid doors' series, then sliding), never one of ``exclude_families`` (the facade's), the look of the
    house's style (``look_fit``), the house's ``seed`` among equal families. Each entry carries ``inside: True`` (the
    build centres it in the wall), ``role``, ``outward`` (into the room it opens into), ``mirror`` / ``hinge``
    (``hinge_mirror``) and ``add_handles`` (the audit sees no handle). ``notes`` gets the left-out models per role and
    a ``parametric`` record (with the reason) per door left to the parametric build.

    29 Oct 2026 (user: "Better door models needed"): a pair (``is_pair``) is fitted by its leaf (half its width) and
    built of ``PAIR_LEAVES`` panels of the member (``pair: True``: the build mirrors the leaves so they meet in the
    middle, ``opening_build.pair_mirrors``); a model named for one kind of room (``model_rooms``: "bathroom door") is
    left out of a role whose doors do not all open into such a room."""
    look = look_of(style)
    family = style_family(style)
    seed = house_seed(building) if seed is None else (seed or None)
    notes = notes if notes is not None else []
    out: dict[str, dict] = {}
    by_role: dict[str, list] = {}
    pairs: set = set()
    for rec in inside:
        o = rec["opening"]
        role, why = inside_role(rec, style)
        width = _number(o.get("width")) or 0.0
        height = float(rec["top"]) - float(rec["bottom"])
        if role is None or width <= 0 or height <= 0:
            notes.append({"kind": "parametric", "id": o["id"], "category": INSIDE_CATEGORY,
                          "reason": why if role is None else "no size: the parametric door"})
            continue
        if is_pair(o):
            pairs.add(o["id"])
            width = width / PAIR_LEAVES                  # the leaf a member must fit
        by_role.setdefault(role, []).append((rec, width, height, why))
    base = candidates(extras, INSIDE_CATEGORY, mode)
    cache: dict = {}
    taken: dict[str, str] = {}
    for role in INSIDE_ROLES:
        recs = by_role.get(role) or []
        if not recs:
            continue
        cands, left, look_rank = [], {}, {}
        for e in base:
            named = model_rooms(e)
            off = [r["opening"]["id"] for r, *_ in recs if named and not set(r.get("joins") or ()) & named]
            if off:
                left[e["id"]] = (f"made for a {' / '.join(sorted(named))} (its title): {len(off)} {role} door(s) "
                                 f"open into none ({', '.join(off[:4])})")
                continue
            why = _inside_problem(e, role, family, assets_dir, cache)
            if why is None:
                panes = None
                if assets_dir is not None and look is not None:
                    path = Path(assets_dir) / str(e.get("glb") or "")
                    if ("panes", str(path)) not in cache:
                        cache[("panes", str(path))] = glb_panes(path)
                    panes = cache[("panes", str(path))]
                r, why2 = look_fit(e, look, panes, INSIDE_CATEGORY)
                if r is not None and role == "solid" and look is not None and look["name"] == "period" \
                        and not (_panelled(_title(e)) or model_vision(e).get("leaf") == "panelled"):
                    # = looks.role_door_style: a private room's door in a period style is a panelled leaf
                    r, why2 = r + 1, why2 + "; not panelled: after the panelled leaves of the period look"
                if r is None:
                    why = why2
                else:
                    cands.append(e)
                    look_rank[e["id"]] = (r, why2)
                    continue
            left[e["id"]] = why
        if left:
            notes.append({"kind": "left_out", "category": f"{INSIDE_CATEGORY}:{role}", "models": left})
        openings = [(w, h) for _r, w, h, _why in recs]
        pick = _choose_family(cands, INSIDE_CATEGORY, openings, look_rank, seed and f"{seed}|{role}",
                              set(exclude_families or ()), prefer=taken.get("solid") if role == "glazed" else None)
        if pick is None:
            for rec, w, h, _why in recs:
                notes.append({"kind": "parametric", "id": rec["opening"]["id"], "category": INSIDE_CATEGORY,
                              "role": role, "reason": f"no library {role} inside door fits {w:.2f} x {h:.2f} m: the "
                                                      f"parametric door in the style's look"})
            continue
        _order, key, members, tier = pick
        taken[role] = key
        what = (f"the house's {role} inside door family"
                + ("; the solid doors' series" if role == "glazed" and key == taken.get("solid") else "")
                + (f" (one of {tier} equal families, picked by the house's seed)" if tier > 1 and seed else "")
                + ("; not a facade family" if exclude_families else ""))
        for rec, w, h, why in recs:
            o = rec["opening"]
            fits = [(look_rank[m["id"]][0], f[1], i, m, f) for i, m in enumerate(members)
                    for f in [fit(m, INSIDE_CATEGORY, w, h)] if f is not None]
            if not fits:
                head = members[0]
                notes.append({"kind": "parametric", "id": o["id"], "category": INSIDE_CATEGORY, "role": role,
                              "family": key,
                              "reason": f"no model of the house's {role} inside door family "
                                        f"{str(head.get('title') or head.get('id'))[:40]!r} fits {w:.2f} x {h:.2f} "
                                        f"m: the parametric door keeps the house's door language"})
                continue
            _r, err, _i, e, (n, err) = min(fits, key=lambda t: t[:3])
            pair = o["id"] in pairs
            if pair:
                n = PAIR_LEAVES
            entry = _entry(e, INSIDE_CATEGORY, n, err, w * n if pair else w, h, key, look, look_rank,
                           list(rec["outward"]), f"{what}; {why}")
            if pair:
                mirror, hinge = False, ("a pair: the leaves hinged at the jambs and meeting in the middle (the build "
                                        "mirrors one of them to the model's handle side)")
            else:
                mirror, hinge = hinge_mirror(o, e)
            entry.update(inside=True, role=role, mirror=mirror, hinge=hinge,
                         add_handles=model_handle_side(e) == "none", swing_room=rec.get("swing_room"),
                         swing_assumed=bool(rec.get("swing_assumed")))
            if pair:
                entry.update(pair=True, handle_side=model_handle_side(e))
            out[o["id"]] = entry
    return out


# --------------------------------------------------------------------------
# Argus: door variety (28 Oct 2026)
# --------------------------------------------------------------------------

def _door_rows(doc) -> list[dict]:
    """``[{"id", "category", "family", "model", "title", "role", "inside_model", "statement"}]`` of the doors of a plan
    (``{opening id: entry}``: ``plan`` and ``plan_inside`` merged) or a manifest (``{"objects": [...]}`` or the list
    of manifest objects: a library door's ``library_model`` record, a parametric door's ``door`` record)."""
    rows: dict[str, dict] = {}
    if isinstance(doc, dict) and not isinstance(doc.get("objects"), list):
        for oid, e in doc.items():
            if not isinstance(e, dict) or "category" not in e:
                continue
            asset = e.get("asset") or {}
            rows[str(oid)] = {"id": str(oid), "category": e["category"], "family": e.get("family"),
                              "model": asset.get("asset_id") or asset.get("id"), "title": asset.get("title"),
                              "role": e.get("model_role"), "statement": e.get("statement"),
                              "parametric": False}
        return [r for r in rows.values() if r["category"] != "window"]
    objects = doc.get("objects") if isinstance(doc, dict) else doc
    for ob in objects or []:
        if not isinstance(ob, dict) or ob.get("kind") != "door":
            continue
        oid = str(ob.get("wenart_id") or ob.get("element_id") or ob.get("name"))
        lm = ob.get("library_model") if isinstance(ob.get("library_model"), dict) else None
        if lm is not None:
            rows[oid] = {"id": oid, "category": lm.get("category"), "family": lm.get("family") or lm.get("asset_id"),
                         "model": lm.get("asset_id"), "title": lm.get("title"), "role": lm.get("model_role"),
                         "statement": lm.get("statement"), "parametric": False}
        elif isinstance(ob.get("door"), dict) and oid not in rows:
            style = ob["door"].get("door_style") or "door"
            rows[oid] = {"id": oid, "category": "entrance" if style == "entrance" else None,
                         "family": f"parametric:{style}", "model": None, "title": f"parametric {style} door",
                         "role": None, "statement": None, "parametric": True}
    return list(rows.values())


def door_variety_problems(doc) -> list[dict]:
    """Argus' door checks of a house (pure; 28 Oct 2026, user: "I want better doors inside the house and the outside
    ... some variation is needed"; lesson UL65): ``[{"target", "message", "severity", "kind"}]`` for a plan
    (``plan`` and ``plan_inside`` merged) or a manifest (``_door_rows``):

    - ``one_door_model`` (major): three or more doors and every one is the same model family;
    - ``inside_door_on_facade`` (major): an outside door whose model is an inside door (its title names one,
      ``INSIDE_WORDS``, or the audit puts it inside);
    - ``no_statement_entrance`` (major): outside doors but no library entrance door, or (minor) an entrance that is
      no statement door or shares its family with another door of the house."""
    rows = _door_rows(doc)
    out: list[dict] = []
    if len(rows) >= 3 and len({r["family"] for r in rows}) == 1:
        r = rows[0]
        out.append({"target": "doors", "kind": "one_door_model", "severity": "major",
                    "message": f"every door of the house ({len(rows)}) is one model ({r['title'] or r['family']}): "
                               "the entrance, the outside doors and the inside doors need their own families (UL65)"})
    outside = [r for r in rows if r["category"] in FACADE_CATEGORIES]
    for r in outside:
        inside_title = _has(f" {str(r.get('title') or '').lower()} ", INSIDE_WORDS)
        if inside_title or r.get("role") == "inside":
            why = "its title names an inside door" if inside_title else "the audit puts the model inside"
            out.append({"target": r["id"], "kind": "inside_door_on_facade", "severity": "major",
                        "message": f"outside door {r['id']} ({r['category']}) has an inside door model "
                                   f"({r['title'] or r['model']}): {why}"})
    entrances = [r for r in rows if r["category"] == "entrance" and not r["parametric"]]
    if outside and not entrances:
        out.append({"target": "entrance", "kind": "no_statement_entrance", "severity": "major",
                    "message": "the house has outside doors but no library entrance door: the entrance needs a "
                               "statement door (UL65)"})
    for r in entrances:
        others = {x["family"] for x in rows if x["id"] != r["id"]}
        if r["family"] in others:
            out.append({"target": r["id"], "kind": "no_statement_entrance", "severity": "minor",
                        "message": f"entrance {r['id']} shares its model family ({r['title'] or r['family']}) with "
                                   "another door of the house: the entrance needs its own statement door"})
        elif r.get("statement") is False:
            out.append({"target": r["id"], "kind": "no_statement_entrance", "severity": "minor",
                        "message": f"entrance {r['id']} ({r['title'] or r['model']}) is no statement door (neither "
                                   "the audit nor its title says front door)"})
    return out


# --------------------------------------------------------------------------
# The doors as built (29 Oct 2026, user: "Better door models needed"; lesson UL89)
# --------------------------------------------------------------------------

# the build's warnings when a planned library opening falls back to the parametric one (``opening_build``): read for a
# manifest written before the parametric opening carried ``library_planned`` (real06 run 20261028-154514-full)
NOT_BUILT_RE = re.compile(r"^(?P<id>[^\s:]+): library (?P<cat>[a-z_]+) not built \((?P<why>.*)\); parametric opening$")
MODEL_FAILED_RE = re.compile(r"^(?P<id>[^\s:]+): library model (?P<file>\S+) (?P<why>.*); parametric opening$")
PARAMETRIC_SHARE_MAX = 1.0 / 3.0       # U18: more of the house's doors than this parametric is a library gap ...
PARAMETRIC_MIN = 2                     # ... once at least this many are


def built_doors(manifest) -> list[dict]:
    """``[{"id", "library", "title", "category", "role", "family", "leaf", "pair", "room_ids", "door", "planned"}]``
    per door of a scene manifest (pure): ``library`` with its ``library_model`` record, else the parametric door with
    its ``door`` record (None: the Milestone 6 door, a slab in a flat frame) and ``planned``: the library model the plan
    chose for it and why the build did not make it (``library_planned``, else the build's warnings)."""
    objects = (manifest or {}).get("objects") if isinstance(manifest, dict) else manifest
    rows: dict[str, dict] = {}
    for ob in objects or []:
        if not isinstance(ob, dict) or ob.get("kind") != "door":
            continue
        oid = str(ob.get("element_id") or ob.get("wenart_id") or ob.get("name"))
        row = rows.setdefault(oid, {"id": oid, "library": False, "title": None, "category": None, "role": None,
                                    "family": None, "leaf": None, "pair": False, "room_ids": [], "door": None,
                                    "planned": None})
        for rid in ob.get("room_ids") or []:
            if rid not in row["room_ids"]:
                row["room_ids"].append(rid)
        lm = ob.get("library_model") if isinstance(ob.get("library_model"), dict) else None
        if lm is not None:
            row.update(library=True, title=lm.get("title"), category=lm.get("category"), role=lm.get("role"),
                       family=lm.get("family") or lm.get("asset_id"), leaf=lm.get("leaf"), pair=bool(lm.get("pair")))
        if isinstance(ob.get("door"), dict):
            row["door"] = ob["door"]
        if isinstance(ob.get("library_planned"), dict):
            row["planned"] = ob["library_planned"]
    warns = (manifest or {}).get("warnings") if isinstance(manifest, dict) else None
    for w in warns or []:
        m = NOT_BUILT_RE.match(str(w)) or MODEL_FAILED_RE.match(str(w))
        row = rows.get(m.group("id")) if m else None
        if row is not None and not row["library"] and row["planned"] is None:
            row["planned"] = {"category": m.groupdict().get("cat"), "why": m.group("why"), "from": "warnings"}
    return list(rows.values())


def is_product_door(door: Optional[dict]) -> bool:
    """A parametric door built as a product (``looks.door_product``): its ``door`` record names an architrave, or it
    hangs on a rail (a sliding or barn door has none) or is a sectional garage door; a solid flush leaf also its face
    detail (29 Oct 2026)."""
    if not isinstance(door, dict):
        return False
    if door.get("surface_mounted") or door.get("door_style") == "sectional":      # a garage door has no architrave
        return True
    if not door.get("architrave"):
        return False
    return door.get("door_style") != "flush" or bool(door.get("leaf_detail"))


def door_product_problems(manifest) -> list[dict]:
    """Model review M20 (pure; module section): ``[{"target", "kind", "severity", "message"}]`` per door of the scene
    that is no real product: ``library_door_not_built`` (major): the plan chose a library model and the build made
    the parametric door (the reason: real06's HSSD doors "CC BY 4.0 without source_url, via (no credit line)");
    ``bare_door`` (major): a parametric door built as a slab (no ``door`` record: the Milestone 6 door) or without its
    architrave and face detail."""
    out = []
    for r in built_doors(manifest):
        if r["library"]:
            continue
        if r["planned"] is not None:
            p = r["planned"]
            what = p.get("title") or p.get("asset_id") or f"its {p.get('category') or 'library'} model"
            out.append({"target": r["id"], "kind": "library_door_not_built", "severity": "major",
                        "message": f"door {r['id']}: the plan chose {what} and the build made the parametric door "
                                   f"instead ({str(p.get('why') or 'no reason recorded')[:200]})"})
        elif not is_product_door(r["door"]):
            style = (r["door"] or {}).get("door_style")
            what = f"a bare parametric {style} door" if style else "the Milestone 6 door (a slab in a flat frame)"
            out.append({"target": r["id"], "kind": "bare_door", "severity": "major",
                        "message": f"door {r['id']} is {what}, no architrave"
                                   + (", no face detail" if style in (None, "flush") else "")
                                   + ": a door no library model fits is built as a product of the house's style"})
    # 29 Oct 2026 (UL122, "Doors looks without frames they need frames"): a library door built with a frame record
    # (``opening_build._door_frame``) that has no lining and no frameless reason stands in a raw hole
    from wenart.blender import door_states as DS

    lib_ids = {r["id"] for r in built_doors(manifest) if r["library"]}
    for p in DS.frame_problems(manifest):
        if p["target"] in lib_ids and p["kind"] == "no_frame" and "no frame record" not in p["message"]:
            out.append({"target": p["target"], "kind": "library_door_without_frame", "severity": "major",
                        "message": p["message"]})
    return out


def door_model_problems(manifest, building: Optional[dict] = None) -> list[dict]:
    """Argus U18 (pure; lesson UL89 "Better door models needed"): ``[{"target", "kind", "severity", "message"}]``:
    ``parametric_doors`` (major): more than ``PARAMETRIC_SHARE_MAX`` of the house's doors (at least
    ``PARAMETRIC_MIN``) are parametric; ``door_for_another_room`` (major): a library door named for a kind of room
    (``model_rooms``: "bathroom door") on a door into none of those rooms (the building's room types)."""
    rows = built_doors(manifest)
    out = []
    para = [r["id"] for r in rows if not r["library"]]
    if rows and len(para) >= PARAMETRIC_MIN and len(para) > PARAMETRIC_SHARE_MAX * len(rows):
        refused = [r["id"] for r in rows if not r["library"] and r["planned"] is not None]
        out.append({"target": "doors", "kind": "parametric_doors", "severity": "major",
                    "message": f"{len(para)} of the house's {len(rows)} doors are the parametric door "
                               f"({', '.join(para[:8])}{' ...' if len(para) > 8 else ''})"
                               + (f"; {len(refused)} of them had a library model the build did not make "
                                  f"({', '.join(refused[:6])})" if refused else "")
                               + ": the audited library doors must reach the build (UL89)"})
    types = {r.get("id"): str(r.get("room_type") or "").lower() for r in (building or {}).get("rooms") or []}
    for r in rows:
        if not r["library"] or not types:
            continue
        named = model_rooms({"title": r["title"]})
        joins = {types.get(x) for x in r["room_ids"]} - {None, ""}
        if named and joins and not joins & named:
            out.append({"target": r["id"], "kind": "door_for_another_room", "severity": "major",
                        "message": f"door {r['id']} into {', '.join(sorted(joins))} has a model made for a "
                                   f"{' / '.join(sorted(named))} ({r['title']}): a door named for one room is no "
                                   "house-wide door"})
    return out
