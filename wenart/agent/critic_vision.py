"""The vision critic (docs/milestone11.md §4, §8 step 2, §14 "vision critic hallucinates").

What: one agent-model call per room and one per exterior view, with a strict JSON-schema answer
``{"findings": [{check, severity, target, message, evidence_image}]}``:

- a room gets up to 4 images: its top-down image (CPU, ``topdown``), up to 2 preview renders of its views and its
  plan crop (when one exists);
- an exterior view gets its preview and, when one exists, the plan crop of its level.

A finding is kept only when its target is a real id of what was shown (the room, a piece of the room, an opening of
the room, a view of the room; for an exterior view: the view id, ``building`` or an exterior wall / opening id),
its evidence image exists, and the code does not contradict it: a finding of a check that code measures alone
(``how: C``) is dropped when that code family ran and found no such violation on the target; a finding equal to
a code finding (same check and target) is dropped as a duplicate. Every dropped finding is returned with the
reason (the loop logs it).

Why: the model only proposes; code checks decide (CLAUDE.md evidence rules). One pass at temperature 0 replaces
the two-pass rule because every finding is checked by code (M11 D8).

How: ``critique(model, ...)`` is pure apart from the model call and the top-down PNG; prompts in ``prompts``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from wenart.agent import critic_code as CC
from wenart.agent import prompts as P
from wenart.agent.model import MAX_IMAGES, user_message


def answer_schema(checks) -> dict:
    return {"type": "object", "additionalProperties": False, "required": ["findings"],
            "properties": {"findings": {"type": "array", "maxItems": 12, "items": {
                "type": "object", "additionalProperties": False,
                "required": ["check", "severity", "target", "message", "evidence_image"],
                "properties": {"check": {"enum": list(checks)}, "severity": {"enum": list(P.SEVERITIES)},
                               "target": {"type": "string", "minLength": 1, "maxLength": 80},
                               "message": {"type": "string", "minLength": 3, "maxLength": 300},
                               "evidence_image": {"type": "integer", "minimum": 1, "maximum": MAX_IMAGES}}}}}}


ROOM_SCHEMA = answer_schema(P.ROOM_CHECKS)
EXTERIOR_SCHEMA = answer_schema(P.EXTERIOR_CHECKS)


def room_ids(building: dict, room_id: str, views: list[str]) -> set:
    from wenart.furniture import placer
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    ids = {room_id} | set(views)
    if room is None:
        return ids
    ids |= {f.get("id") for f in building.get("furniture") or [] if f.get("room_id") == room_id}
    try:
        doors, windows = placer.room_openings(building, room)
        ids |= {o.get("id") for o in doors + windows}
    except Exception:  # noqa: BLE001 - a room without a usable polygon: no opening ids
        pass
    return {i for i in ids if i}


def exterior_ids(building: dict, view: str) -> set:
    ids = {view, "building"}
    ids |= {w.get("id") for w in building.get("walls") or [] if w.get("exterior")}
    ext_walls = {w.get("id") for w in building.get("walls") or [] if w.get("exterior")}
    ids |= {o.get("id") for o in building.get("openings") or [] if o.get("wall_id") in ext_walls}
    return {i for i in ids if i}


def screen(answer: Optional[dict], allowed: set, n_images: int, code: dict, room_id: Optional[str],
           source: str = "vision", call_id: str = "") -> tuple[list[dict], list[dict]]:
    """``(kept, dropped)`` findings of one answer (module docstring rules)."""
    kept, dropped = [], []
    ran = CC.measured(code)
    code_hits = {(f["check"], f["target"]) for f in code.get("findings") or []}
    for i, item in enumerate((answer or {}).get("findings") or []):
        f = {"id": f"v:{call_id}:{i + 1}", "source": source, "check": item.get("check"),
             "severity": item.get("severity"), "target": item.get("target"), "room_id": room_id,
             "message": item.get("message"), "evidence": {"image": item.get("evidence_image"), "call_id": call_id}}
        why = None
        if item.get("target") not in allowed:
            why = f"target {item.get('target')!r} is not an id of what was shown"
        elif not 1 <= int(item.get("evidence_image") or 0) <= n_images:
            why = f"evidence image {item.get('evidence_image')} does not exist ({n_images} images)"
        elif (item.get("check"), item.get("target")) in code_hits:
            why = "duplicate of a code finding"
        elif P.CHECKLIST.get(item.get("check"), {}).get("how") == "C" and CC.FAMILY_OF.get(item.get("check")) in ran:
            why = f"code contradicts: {item.get('check')} measured by code without a violation on {item.get('target')}"
        if why:
            f["dropped"] = why
            dropped.append(f)
        else:
            kept.append(f)
    return kept, dropped


def critique_room(model, building: dict, room_id: str, *, previews: list[tuple[str, Path]],
                  topdown: Optional[Path], plan_crop: Optional[Path], code: dict, call_id: str) -> dict:
    """One room: ``{"kept", "dropped", "error", "images"}``."""
    room = next(r for r in building.get("rooms") or [] if r.get("id") == room_id)
    images, labels = [], []
    if topdown is not None:
        images.append(topdown)
        labels.append("top-down plan of the room as built (pieces, fronts, doors, windows)")
    for view, path in previews[:2]:
        images.append(path)
        labels.append(f"render of view {view}")
    if plan_crop is not None and len(images) < MAX_IMAGES:
        images.append(plan_crop)
        labels.append("crop of the source drawing (what the architect drew)")
    from wenart.furniture import placer
    try:
        doors, windows = placer.room_openings(building, room)
    except Exception:  # noqa: BLE001
        doors, windows = [], []
    pieces = [f for f in building.get("furniture") or [] if f.get("room_id") == room_id]
    room_code = [f for f in code.get("findings") or [] if f.get("room_id") == room_id]
    prompt = P.room_critic_prompt(room, pieces, doors + windows, [v for v, _ in previews], labels, room_code)
    messages = [{"role": "system", "content": P.CRITIC_SYSTEM},
                user_message(prompt, images, [f"Image {i + 1}: {lab}" for i, lab in enumerate(labels)])]
    reply = model.critic(messages, ROOM_SCHEMA, call_id=call_id)
    if reply.data is None:
        return {"kept": [], "dropped": [], "error": "; ".join(reply.errors[:3]) or "no answer", "images": images}
    kept, dropped = screen(reply.data, room_ids(building, room_id, [v for v, _ in previews]), len(images), code,
                           room_id, call_id=call_id)
    return {"kept": kept, "dropped": dropped, "error": None, "images": images}


def critique_exterior(model, building: dict, view: str, *, preview: Path, plan_crop: Optional[Path], code: dict,
                      call_id: str) -> dict:
    images, labels = [preview], [f"render of exterior view {view}"]
    if plan_crop is not None:
        images.append(plan_crop)
        labels.append("crop of the source drawing")
    levels = len(building.get("levels") or [])
    note = f"The building has {levels} level(s); roof: {(building.get('roof') or {}).get('type', 'unknown')}."
    ids = exterior_ids(building, view)
    ext_code = [f for f in code.get("findings") or [] if f.get("check", "").startswith("X") or f.get("target") == view]
    prompt = P.exterior_critic_prompt(view, note, sorted(ids)[:60], labels, ext_code)
    messages = [{"role": "system", "content": P.CRITIC_SYSTEM},
                user_message(prompt, images, [f"Image {i + 1}: {lab}" for i, lab in enumerate(labels)])]
    reply = model.critic(messages, EXTERIOR_SCHEMA, call_id=call_id)
    if reply.data is None:
        return {"kept": [], "dropped": [], "error": "; ".join(reply.errors[:3]) or "no answer", "images": images}
    kept, dropped = screen(reply.data, ids, len(images), code, None, call_id=call_id)
    return {"kept": kept, "dropped": dropped, "error": None, "images": images}
