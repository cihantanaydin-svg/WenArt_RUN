"""The agent's overrides the build reads (docs/milestone11.md §2, §3.2, contract §17.3).

What: ``building["agent_overrides"] = {"cameras": [...], "exterior": {...}, "materials": {...}, "round": n}`` (the
accepted edits of the agent, track A) read into the parts of the build they change:

- ``cameras``: ``{action: set | add | remove, view_id, kind: interior | exterior, room_id, position [x, y, z],
  target [x, y, z], lens_mm, reason}``. ``set`` replaces the searched (or planned) camera ``view_id`` by this fixed
  camera (a ``view_id`` that does not exist is added), ``add`` adds it, ``remove`` drops it
  (``apply_cameras``). A fixed camera keeps the given position, target and lens, no lens shift; its record has
  ``policy: agent`` and ``placement`` = the reason.
- ``exterior``: ``{roof: {type, pitch_deg, overhang_m}, ground: look_id, site: {path, fence, trees, front_court},
  sun: {azimuth_deg, elevation_deg}}`` (every key optional): the roof through ``roof.apply_override``, the ground
  look over the garden look (``apply_looks``), the site options over the brief's (``site_options``), the sun
  over the style's lighting (``apply_sun``: azimuth in compass degrees clockwise from north, as the style).
- ``materials``: ``{slot: look_id}`` over ``style.json`` (``apply_style``: the inside slots) and over the
  resolved outside looks (``apply_looks``).

Why: the agent never edits the building JSON's geometry or a ``.blend``; the build replays its accepted edits, so
a re-run is deterministic and ``--no-orchestrator`` (no ``agent_overrides``) builds what M10 built.

How: pure Python (Blender's Python runs it too); every function returns its input unchanged when there is no
override, and lists what it applied (the scene manifest's ``agent_overrides``).
"""
from __future__ import annotations

import copy
import math
from typing import Optional, Sequence

CAMERA_ACTIONS = ("set", "add", "remove")
CAMERA_KINDS = ("interior", "exterior")
# Material slots of the agent's set_material (§3.2): the style slots inside, the resolved looks outside.
STYLE_SLOTS = ("walls", "floor", "ceiling", "wet_walls", "wet_floor", "kitchen_walls", "splashback", "trim", "door",
               "window_frame")
LOOK_SLOTS = ("facade", "roof", "window_frame", "door", "paving", "garden", "ground", "plot_wall", "plinth",
              "cornice", "surround", "hedge", "path")
SLOT_ALIASES = {"frames": "window_frame", "window_frames": "window_frame", "kitchen_splashback": "splashback",
                "wet_room_walls": "wet_walls", "wet_room_floor": "wet_floor"}
SITE_KEYS = ("path", "fence", "trees", "front_court")


def overrides_of(building: dict) -> Optional[dict]:
    """The building's ``agent_overrides`` when it holds anything, else None (the M10 build)."""
    ov = building.get("agent_overrides") if isinstance(building, dict) else None
    if not isinstance(ov, dict):
        return None
    if not (ov.get("cameras") or ov.get("exterior") or ov.get("materials")):
        return None
    return ov


def exterior_of(building: dict) -> dict:
    ov = overrides_of(building) or {}
    return ov.get("exterior") if isinstance(ov.get("exterior"), dict) else {}


def roof_override(building: dict) -> Optional[dict]:
    """The roof override (``roof.override_of``: the same reader the vision check uses)."""
    from wenart.blender.roof import override_of

    return override_of(building)


def slot_name(slot: str) -> str:
    return SLOT_ALIASES.get(str(slot), str(slot))


def materials_of(building: dict) -> dict:
    """``{slot: look_id}`` of the overrides (aliases resolved; ``exterior.ground`` is the ``ground`` slot)."""
    ov = overrides_of(building) or {}
    out = {slot_name(k): v for k, v in (ov.get("materials") or {}).items() if isinstance(v, str) and v}
    ground = exterior_of(building).get("ground")
    if isinstance(ground, str) and ground and "ground" not in out:
        out["ground"] = ground
    return out


# --------------------------------------------------------------------------
# Cameras
# --------------------------------------------------------------------------

def camera_entries(building: dict, kind: Optional[str] = None) -> list[dict]:
    """The camera entries of the overrides (of one ``kind``; an entry without a kind is interior when it names a
    room, else exterior), in their order."""
    ov = overrides_of(building) or {}
    out = []
    for e in ov.get("cameras") or []:
        if not isinstance(e, dict) or e.get("action") not in CAMERA_ACTIONS or not e.get("view_id"):
            continue
        k = e.get("kind") or ("interior" if e.get("room_id") else "exterior")
        if kind is None or k == kind:
            out.append(dict(e, kind=k))
    return out


def fixed_plan(entry: dict, level_id: Optional[str] = None, index: int = 1, base: Optional[dict] = None) -> dict:
    """The camera plan of a ``set`` / ``add`` entry: the given position, target and lens (``base``'s lens, else 18 mm
    inside and 26 mm outside), no lens shift, sensor and resolution as the searched cameras."""
    from wenart.blender import cameras

    kind = entry.get("kind") or "interior"
    lens = entry.get("lens_mm") or (base or {}).get("lens_mm") or (cameras.LENS_MM if kind == "interior" else 26.0)
    pos = [float(v) for v in entry["position"]]
    tgt = [float(v) for v in entry["target"]]
    pitch = math.degrees(math.atan2(tgt[2] - pos[2], math.hypot(tgt[0] - pos[0], tgt[1] - pos[1])))
    plan = {"name": str(entry["view_id"]), "kind": kind, "room_id": entry.get("room_id") if kind == "interior" else None,
            "level_id": level_id if kind == "interior" else None, "index": index, "position": pos, "target": tgt,
            "lens_mm": float(lens), "lens_rule": "agent", "sensor_mm": cameras.SENSOR_MM,
            "resolution": list(cameras.RESOLUTION), "shift_x": 0.0, "shift_y": 0.0, "policy": "agent",
            "score": None, "pitch_deg": round(pitch, 2), "placement": f"agent override: {entry.get('reason') or ''}".strip(),
            "anchor": None, "warning": None, "visible_openings": [], "visible_furniture": [],
            "status": "assumed", "dropped_reason": None, "agent": {"action": entry["action"],
                                                                    "reason": entry.get("reason")}}
    if kind == "exterior":
        plan.update(view=(base or {}).get("view") or "agent", sides=list((base or {}).get("sides") or []),
                    region_id=(base or {}).get("region_id"), variant=(base or {}).get("variant"))
    return plan


def apply_cameras(plans: list[dict], entries: Sequence[dict], level_id: Optional[str] = None,
                  rooms: Optional[set] = None) -> tuple[list[dict], list[dict]]:
    """``(plans, applied)``: the planned cameras with the override entries applied in order (pure). ``set``
    replaces the plan of the same name (added when there is none), ``add`` adds a plan (replacing one of the same
    name), ``remove`` drops it. Interior entries apply on their room's level (``rooms``: the room ids of
    ``level_id``; None = every entry). ``applied``: ``{"view_id", "action", "kind", "result": replaced | added |
    removed | not found, "reason"}``."""
    out = list(plans)
    applied = []
    for e in entries:
        if e.get("kind") == "interior" and rooms is not None and e.get("room_id") not in rooms:
            continue
        name = str(e["view_id"])
        at = next((i for i, p in enumerate(out) if p.get("name") == name), None)
        rec = {"view_id": name, "action": e["action"], "kind": e.get("kind"), "reason": e.get("reason")}
        if e["action"] == "remove":
            if at is None:
                rec["result"] = "not found"
            else:
                out.pop(at)
                rec["result"] = "removed"
            applied.append(rec)
            continue
        if not (isinstance(e.get("position"), (list, tuple)) and len(e["position"]) == 3
                and isinstance(e.get("target"), (list, tuple)) and len(e["target"]) == 3):
            rec["result"] = "not applied: no position or target"
            applied.append(rec)
            continue
        base = out[at] if at is not None else None
        index = (base or {}).get("index") or (1 + sum(1 for p in out if p.get("room_id") == e.get("room_id")))
        plan = fixed_plan(e, level_id, index, base)
        if at is None:
            out.append(plan)
            rec["result"] = "added"
        else:
            out[at] = plan
            rec["result"] = "replaced"
        applied.append(rec)
    return out, applied


# --------------------------------------------------------------------------
# Materials, looks, sun, site
# --------------------------------------------------------------------------

def look_entry(look_id: str) -> dict:
    """A style slot / look of a vocabulary slug (its asset; the colour of the slot is dropped: the look is the
    agent's choice)."""
    try:
        from wenart.style.profile import asset_of
        asset = asset_of(look_id)
    except ImportError:
        asset = None
    return {"material": look_id, "asset": asset, "colour": None}


def apply_style(style: dict, materials: dict) -> tuple[dict, list[dict]]:
    """``(style, applied)``: the style with the inside slots of ``materials`` replaced (pure; a copy when anything
    changes). ``window_frame`` also sets the frame's outside look."""
    applied = []
    if not materials:
        return style, applied
    out = copy.deepcopy(style)
    for slot, look_id in materials.items():
        slot = slot_name(slot)
        if slot not in STYLE_SLOTS:
            continue
        entry = look_entry(look_id)
        was = (style.get(slot) or {}).get("material") if isinstance(style.get(slot), dict) else None
        if slot == "window_frame":
            entry["outside"] = {"material": look_id, "colour": None}
        out[slot] = dict(out.get(slot) or {}, **entry) if isinstance(out.get(slot), dict) else entry
        applied.append({"slot": slot, "look_id": look_id, "was": was, "target": "style"})
    return out, applied


def apply_looks(looks: Optional[dict], materials: dict) -> tuple[Optional[dict], list[dict]]:
    """``(looks, applied)``: the resolved outside looks (``exterior.resolve_looks``) with the outside slots of
    ``materials`` replaced (source ``agent``, not assumed); ``ground`` sets the garden look (the ground's)."""
    applied = []
    if not looks or not materials:
        return looks, applied
    out = dict(looks)
    for slot, look_id in materials.items():
        slot = slot_name(slot)
        target = "garden" if slot == "ground" else slot
        if slot not in LOOK_SLOTS:
            continue
        was = (looks.get(target) or {}).get("material")
        entry = look_entry(look_id)
        out[target] = {"material": look_id, "colour": None, "rgb": None, "asset": entry["asset"], "source": "agent",
                       "assumed": False, "reason": "agent override (docs/milestone11.md §17.3)", "evidence": []}
        applied.append({"slot": target, "look_id": look_id, "was": was, "target": "looks"})
    return out, applied


def apply_sun(style: dict, building: dict) -> tuple[dict, Optional[dict]]:
    """``(style, applied)``: the style's lighting with the override's sun (``exterior.sun``: ``azimuth_deg`` compass
    clockwise from north as the style's, ``elevation_deg`` above the horizon)."""
    sun = exterior_of(building).get("sun")
    if not isinstance(sun, dict) or not sun:
        return style, None
    lighting = dict(style.get("lighting") or {})
    applied = {}
    for key, field in (("azimuth_deg", "sun_azimuth_deg"), ("elevation_deg", "sun_elevation_deg")):
        v = sun.get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            applied[key] = {"value": float(v), "was": lighting.get(field)}
            lighting[field] = float(v)
    if not applied:
        return style, None
    lighting["sun_source"] = "agent"
    return dict(style, lighting=lighting), applied


def site_options(building: dict, front_court: str = "auto") -> dict:
    """The site options of the build (pure): ``{"path": bool, "fence": hedge | fence | none, "trees": int,
    "front_court": auto | yes | no, "source": {key: brief | default | agent}}``; the brief's ``front_court``
    (D6), the override's ``exterior.site`` on top."""
    out = {"path": True, "fence": "hedge", "trees": 3, "front_court": front_court if front_court in ("auto", "yes", "no")
           else "auto", "source": {"path": "default", "fence": "default", "trees": "default", "front_court": "brief"}}
    site = exterior_of(building).get("site")
    if not isinstance(site, dict):
        return out
    if isinstance(site.get("path"), bool):
        out["path"], out["source"]["path"] = site["path"], "agent"
    fence = site.get("fence")
    if isinstance(fence, bool):
        fence = "hedge" if fence else "none"
    if fence in ("hedge", "fence", "none"):
        out["fence"], out["source"]["fence"] = fence, "agent"
    trees = site.get("trees")
    if isinstance(trees, bool):
        trees = 3 if trees else 0
    if isinstance(trees, int) and 0 <= trees <= 12:
        out["trees"], out["source"]["trees"] = trees, "agent"
    fc = site.get("front_court")
    if isinstance(fc, bool):
        fc = "yes" if fc else "no"
    if fc in ("auto", "yes", "no"):
        out["front_court"], out["source"]["front_court"] = fc, "agent"
    return out
