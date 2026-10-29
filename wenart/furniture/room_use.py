"""M21: the rooms furnished for their use (29 Oct 2026, the user's review of real06 run 20261028-154514-full).

One model-review check (M21) and one Argus lessons check (U19, ``wenart.audit.lessons``) over what the user asked
for on 29 Oct 2026, measured on the building as built (pure; shapely):

- a TV in every living room and in the master bedroom, on a TV unit facing the seat (``media_wall.review``; UL99);
- the furniture density of living and dining rooms, a bookshelf in living rooms and studies, books on every
  bookshelf, storage in every bathroom (``room_fill.review``; UL98, UL103, UL107, UL102);
- no library model the user rejected (``rejected_models``: ``catalog.user_rejection``; UL94), and no drawn floor
  lamp built at its oversized plan symbol (``symbol_sizes``: ``sizes.SYMBOL_MAX_M``; UL94).

Every finding names its rule and lesson in ``metrics`` (``rule``, ``lesson``). The ceiling lights' spacing (UL91) is
the lighting rule's own check (M17, ``ceiling_lights.review``).
"""
from __future__ import annotations

from typing import Optional

REVIEW_CHECK = "M21"


def rejected_models(building: dict) -> list[dict]:
    """A built piece or decor item whose library model the user rejected (major)."""
    from wenart.furniture import catalog as C

    out = []
    for kind in ("furniture", "decor"):
        for f in building.get(kind) or []:
            asset = f.get("asset") if isinstance(f.get("asset"), dict) else None
            if not asset or f.get("build") is False:
                continue
            rec = C.user_rejection(asset)
            if rec is None:
                continue
            out.append({"check": REVIEW_CHECK, "severity": "major", "target": f.get("id"), "room_id": f.get("room_id"),
                        "message": (f"{f.get('id')} ({f.get('type')}) is built with {asset.get('asset_id')}, a model "
                                    f"the user rejected on {rec.get('date')}: \"{rec.get('user')}\""),
                        "metrics": {"model_review": True, "rule": "user_rejected", "lesson": rec.get("lesson") or
                                    "UL94", "asset_id": asset.get("asset_id")}})
    return out


def symbol_sizes(building: dict) -> list[dict]:
    """A drawn piece of a symbol type (a floor lamp) built wider than its type takes from above (minor): its model was
    fitted to the drawn plan symbol, not to a real product (``fit.apply_size_snap`` snaps it since 29 Oct 2026)."""
    from wenart.furniture import sizes as SZ

    out = []
    for f in building.get("furniture") or []:
        cap = SZ.SYMBOL_MAX_M.get(str(f.get("type")))
        if cap is None or f.get("build") is False or not f.get("footprint"):
            continue
        asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        box = asset.get("bbox_m") or f["footprint"].get("size") or []
        if len(box) >= 2 and max(float(box[0]), float(box[1])) > cap + 0.02:
            out.append({"check": REVIEW_CHECK, "severity": "minor", "target": f["id"], "room_id": f.get("room_id"),
                        "message": (f"the {f['type'].replace('_', ' ')} {f['id']} is built {float(box[0]):.2f} x "
                                    f"{float(box[1]):.2f} m wide: its plan symbol's size, larger than a real "
                                    f"{f['type'].replace('_', ' ')} ({cap:.2f} m at most from above)"),
                        "metrics": {"model_review": True, "rule": "symbol_size", "lesson": "UL94", "cap_m": cap}})
    return out


def review(building: dict, brief: Optional[dict] = None) -> tuple[list[dict], int]:
    """M21 (pure): ``(findings, checked)`` of every part (module docstring)."""
    from wenart.furniture import media_wall as MW
    from wenart.furniture import room_fill as RF

    got, n = MW.review(building, brief)
    more, m = RF.review(building)
    rejected = rejected_models(building)
    symbols = symbol_sizes(building)
    pieces = len([f for f in building.get("furniture") or [] if f.get("build") is not False])
    return got + more + rejected + symbols, n + m + pieces
