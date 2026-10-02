"""Model calls of the vision check: what to ask, the resumable answers file, the run loop (§5.3-5.7).

What:

- ``CallSpec``: one call = one image kind of one camera for one model:
  the images (render first; the plan crop second for ``plan_ab``), the text
  labels before them, the prompt, the strict schema, the labelled items and
  ``input_sha256`` (prompt, schema, labels, image bytes, model id).
- Image kinds (§5.7): ``cycles``; ``polished`` (the polish final attempt);
  ``removal:<id>`` (the control render without the element, asked about the
  original list); ``insertion:<id>`` (the normal render, asked about the
  list recomputed from the control render: must report an extra there);
  ``swap:<id>`` (the normal render, one required furniture type replaced:
  must come back different/absent); ``plan_ab:<cam>`` (Cycles render + the
  source-plan crop as Image 2) and ``plan_ab:removal:<id>`` (control render +
  plan crop; added so the A/B can measure removal detection with the plan);
  ``polished`` / ``sweep:a<k>`` for the realism preference (both orders).
- ``AnswerStore``: ``check/answers_<slug>.json`` = ``{schema_version,
  model_key, model, slug, incomplete, calls: {<call_key>: {camera,
  image_kind, prompt_kind: check|plan_ab|preference, order, prompt,
  raw_text, data, latency_s, error, input_sha256, labels, images, ...}}}``,
  rewritten after every call. A call is reused when its key, input hash
  and answer are there; a failed or stale one is asked again.
- ``run_specs``: the loop with ``--deadline`` (no new call after it; the
  file gets ``incomplete: true``).

The call key is ``<prompt_kind>|<camera>|<image_kind>`` (``|<order>`` for the
preference); the inputs live in ``input_sha256``, so a re-rendered image or a
changed list makes the stored answer stale instead of silently reused.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from wenart import views
from wenart.vision_check import preference as R
from wenart.vision_check import prompts as P
from wenart.vision_check import schemas as S
from wenart.vision_check.project import Project, read_json, rel, write_json

PROMPT_KINDS = ("check", "plan_ab", "preference")
RUN_KINDS = ("cycles", "polished", "controls", "plan_ab")
PREFERENCE_KINDS = ("polished", "sweep")
ORDERS = R.ORDERS


class UsageError(ValueError):
    """A wrong ``--kinds`` or model key: the CLI prints it and exits 2."""


@dataclass
class CallSpec:
    key: str
    camera: str
    image_kind: str
    prompt_kind: str
    prompt: str
    schema: dict
    images: list
    image_labels: list
    size: tuple
    items: list = field(default_factory=list)
    decoy: Optional[dict] = None
    order: Optional[str] = None
    expected: Optional[dict] = None
    base_view: Optional["views.View"] = None
    target: Optional[str] = None
    target_box_px: Optional[list] = None
    input_sha256: str = ""

    def labels_map(self) -> dict:
        return {it["label"]: ("decoy" if it["decoy"] else it["wenart_id"]) for it in self.items}


def call_key(prompt_kind: str, camera: str, image_kind: str, order: Optional[str] = None) -> str:
    return "|".join([prompt_kind, camera, image_kind] + ([order] if order else []))


def kind_slug(image_kind: str) -> str:
    """Image kind as a file-name part (``removal:f_1`` -> ``removal-f_1``)."""
    return image_kind.replace(":", "-")


# --------------------------------------------------------------------------
# Specs
# --------------------------------------------------------------------------

def _decoy(project: Project, base_view: "views.View", exp: dict) -> Optional[dict]:
    dcfg = project.cfg["decoy"]

    def place():
        index, depth = project.maps(base_view)
        return P.place_decoy(index, depth, tuple(dcfg["box_frac"]), float(dcfg["min_bare_frac"]),
                             float(dcfg["step_frac"]))

    box = project.cached(("decoy_box", str(base_view.index), str(base_view.depth_mm)), place)
    if box is None:
        return None
    room_id = exp.get("room_id")
    present = {p.get("type") for p in project.building.get("furniture") or [] if p.get("room_id") == room_id}
    present |= {e.get("type") for e in exp.get("elements") or []}
    dtype = P.decoy_type(exp.get("room_type"), present, dcfg["fallback_types"])
    if dtype is None:
        return None
    W, H = base_view.size
    return {"type": dtype, "box_px": box, "box_1000": views.box_to_1000(box, W, H)}


def _finish(project: Project, spec: CallSpec, model: str) -> CallSpec:
    payload = {"prompt": spec.prompt, "schema": spec.schema, "labels": spec.image_labels,
               "images": [project.file_sha(p) for p in spec.images], "model": model,
               "items": spec.labels_map()}
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    spec.input_sha256 = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return spec


def check_spec(project: Project, camera: str, image_kind: str, model: str = "") -> Optional[CallSpec]:
    """The element-check call of one image kind of one camera, or None when its inputs are missing."""
    vs = project.views()
    if camera not in vs:
        return None
    view = vs[camera]
    exp = project.expected(camera)
    base_view, image, swap, target, target_box = view, view.png, None, None, None
    prompt_kind, plan = "check", None
    kind = image_kind
    if kind.startswith("plan_ab:"):
        prompt_kind = "plan_ab"
        plan = project.plan_path(camera)
        if not plan.is_file():
            return None
        kind = image_kind[len("plan_ab:"):]
        if kind == camera:
            kind = "cycles"
    if kind == "cycles":
        pass
    elif kind == "polished":
        pol = project.polished().get(camera)
        if not pol:
            return None
        image = pol["png"]
    elif kind.startswith(("removal:", "insertion:")):
        cid = kind.split(":", 1)[1]
        control = next((c for c in project.controls() if c["id"] == cid and c["camera"] == camera), None)
        if control is None:
            return None
        hidden = project.control_view(control)
        if hidden is None:
            return None
        target = cid
        if kind.startswith("removal:"):
            image = hidden.png
        else:
            exp = project.expected_of(hidden)
            base_view = hidden
            target_box = next((e["box_px"] for e in project.expected(camera)["elements"]
                               if e["wenart_id"] == cid), None)
    elif kind.startswith("swap:"):
        sid = kind.split(":", 1)[1]
        swap_entry = next((s for s in project.swaps() if s["id"] == sid and s["camera"] == camera), None)
        if swap_entry is None:
            return None
        swap = {"id": sid, "type": swap_entry["swap_to"]}
        target = sid
    else:
        raise ValueError(f"unknown image kind {image_kind!r}")
    decoy = _decoy(project, base_view, exp)
    items = P.check_items(exp, decoy, swap)
    room = project.room(exp.get("room_id"))
    size = tuple(view.size)
    text = P.check_prompt(items, room.get("label") or exp.get("room_id"), exp.get("room_type"), size,
                          plan_ab=plan is not None)
    images = [image] + ([plan] if plan is not None else [])
    labels = [P.IMAGE_LABEL] + ([P.PLAN_LABEL] if plan is not None else [])
    spec = CallSpec(key=call_key(prompt_kind, camera, image_kind), camera=camera, image_kind=image_kind,
                    prompt_kind=prompt_kind, prompt=text, schema=S.view_schema([it["label"] for it in items]),
                    images=images, image_labels=labels, size=size, items=items, decoy=decoy, expected=exp,
                    base_view=base_view, target=target, target_box_px=target_box)
    return _finish(project, spec, model)


def preference_spec(project: Project, camera: str, image_kind: str, order: str, model: str = ""
                    ) -> Optional[CallSpec]:
    """One realism-preference call (§5.6): ``order`` ``pc`` = polished first, ``cp`` = Cycles first."""
    vs = project.views()
    if camera not in vs or order not in ORDERS:
        return None
    if image_kind == "polished":
        pol = project.polished().get(camera)
        png = pol["png"] if pol else None
    elif image_kind.startswith("sweep:a"):
        k = int(image_kind[len("sweep:a"):])
        png = next((a["png"] for a in project.sweep_attempts().get(camera, []) if a["k"] == k), None)
    else:
        raise ValueError(f"no preference for image kind {image_kind!r}")
    if png is None:
        return None
    images = [png, vs[camera].png] if order == "pc" else [vs[camera].png, png]
    spec = CallSpec(key=call_key("preference", camera, image_kind, order), camera=camera, image_kind=image_kind,
                    prompt_kind="preference", prompt=R.PROMPT, schema=R.schema(),
                    images=images, image_labels=list(R.LABELS), size=tuple(vs[camera].size),
                    order=order)
    return _finish(project, spec, model)


def check_kinds(project: Project, kinds, warn: bool = True) -> list[tuple[str, str]]:
    """``[(camera, image_kind)]`` of the element checks asked for (``cycles,polished,controls,plan_ab``)."""
    kinds = list(kinds)
    unknown = [k for k in kinds if k not in RUN_KINDS]
    if unknown:
        raise UsageError(f"unknown --kinds {unknown}; choose from {', '.join(RUN_KINDS)}")
    out: list[tuple[str, str]] = []
    cams = list(project.views())
    if "cycles" in kinds:
        out += [(c, "cycles") for c in cams]
    if "polished" in kinds:
        pol = project.polished()
        out += [(c, "polished") for c in cams if c in pol]
    if "controls" in kinds:
        for c in project.controls():
            out += [(c["camera"], f"removal:{c['id']}"), (c["camera"], f"insertion:{c['id']}")]
        out += [(s["camera"], f"swap:{s['id']}") for s in project.swaps()]
    if "plan_ab" in kinds:
        ab = project.plan_ab_cameras()
        for cam in ab:
            if project.plan_path(cam).is_file():
                out.append((cam, f"plan_ab:{cam}"))
            elif warn:
                project.warn(f"plan A/B: no plan crop for {cam} (run plan-crops)")
        for c in project.controls():
            if c["camera"] in ab and project.plan_path(c["camera"]).is_file():
                out.append((c["camera"], f"plan_ab:removal:{c['id']}"))
    return out


def preference_kinds(project: Project, kinds) -> list[tuple[str, str, str]]:
    """``[(camera, image_kind, order)]`` of the preference calls (``polished`` and/or ``sweep``)."""
    out = []
    for kind in kinds:
        if kind not in PREFERENCE_KINDS:
            raise UsageError(f"unknown preference kind {kind!r}; choose from {', '.join(PREFERENCE_KINDS)}")
        if kind == "polished":
            for cam in project.polished():
                out += [(cam, "polished", o) for o in ORDERS]
        else:
            for cam, attempts in project.sweep_attempts().items():
                for a in attempts:
                    out += [(cam, f"sweep:a{a['k']}", o) for o in ORDERS]
    return out


def build_specs(project: Project, check: list, prefs: list, model: str = "") -> list[CallSpec]:
    specs = []
    for cam, kind in check:
        spec = check_spec(project, cam, kind, model)
        if spec is not None:
            specs.append(spec)
    for cam, kind, order in prefs:
        spec = preference_spec(project, cam, kind, order, model)
        if spec is not None:
            specs.append(spec)
    return specs


# --------------------------------------------------------------------------
# Answers file
# --------------------------------------------------------------------------

def answers_path(check_dir: Path, slug: str) -> Path:
    return Path(check_dir) / f"answers_{slug}.json"


class AnswerStore:
    """``check/answers_<slug>.json``: every call of one model, rewritten after each call."""

    def __init__(self, path: Path, model_key: str, slug: str, model: str = "") -> None:
        self.path = Path(path)
        data = read_json(self.path) or {}
        self.data = {"schema_version": "0.1", "model_key": model_key, "model": data.get("model") or model,
                     "slug": slug, "incomplete": bool(data.get("incomplete", False)),
                     "calls": dict(data.get("calls") or {})}
        if model:
            self.data["model"] = model

    @property
    def calls(self) -> dict:
        return self.data["calls"]

    def get(self, key: str) -> Optional[dict]:
        return self.calls.get(key)

    def valid(self, spec: CallSpec) -> Optional[dict]:
        """The stored record of ``spec`` when it is current (same inputs) and answered, else None."""
        rec = self.calls.get(spec.key)
        if rec and rec.get("input_sha256") == spec.input_sha256 and rec.get("data") is not None:
            return rec
        return None

    def put(self, key: str, record: dict) -> None:
        self.calls[key] = record
        self.save()

    def save(self) -> None:
        write_json(self.path, self.data)


def record_of(spec: CallSpec, result, check_dir: Path, model: str, seed: int) -> dict:
    return {
        "camera": spec.camera, "image_kind": spec.image_kind, "prompt_kind": spec.prompt_kind, "order": spec.order,
        "prompt": spec.prompt, "raw_text": result.raw_text, "data": result.data,
        "latency_s": round(float(result.latency_s), 3), "error": result.error, "attempts": result.attempts,
        "input_sha256": spec.input_sha256, "labels": spec.labels_map(),
        "images": [rel(p, check_dir) for p in spec.images], "model": model, "seed": seed,
        "decoy": spec.decoy,
    }


def run_specs(specs: list[CallSpec], store: AnswerStore, client, *, deadline: Optional[float] = None,
              seed: int = 0, max_side: Optional[int] = None, log: Callable = print,
              clock: Callable[[], float] = time.time) -> dict:
    """Ask every spec that has no current answer; stop starting calls after ``deadline`` (epoch s).

    Returns ``{"asked", "reused", "failed", "left", "incomplete"}``. The
    answers file is written after every call and at the end.
    """
    stats = {"asked": 0, "reused": 0, "failed": 0, "left": 0, "incomplete": False}
    model = getattr(client, "model", "") or store.data.get("model") or ""
    for i, spec in enumerate(specs):
        if store.valid(spec) is not None:
            stats["reused"] += 1
            continue
        if deadline is not None and clock() >= deadline:
            stats["left"] = sum(1 for s in specs[i:] if store.valid(s) is None)
            stats["incomplete"] = True
            log(f"vision_check: deadline reached, {stats['left']} call(s) left for the next run")
            break
        result = client.run_schema(list(spec.images), spec.prompt, spec.schema, seed=seed,
                                   task=f"{spec.prompt_kind}:{spec.image_kind}", max_side=max_side,
                                   labels=list(spec.image_labels))
        store.put(spec.key, record_of(spec, result, store.path.parent, str(model), seed))
        stats["asked"] += 1
        if result.data is None:
            stats["failed"] += 1
            log(f"vision_check: {spec.key}: {result.error}")
    store.data["incomplete"] = stats["incomplete"]
    store.data["model"] = str(model) or store.data.get("model")
    store.save()
    return stats
