"""24 Nov 2026 (structure pod gmqln9ca1jiug3, real17): the locked check accepts the bath/shower swap of
``infer.bath_or_shower`` for every bathtub the drawing does not name, also one the vision models typed; a bathtub the
drawing names (a block, a label, a text) keeps its type."""
from __future__ import annotations

import copy

from wenart.furniture import locked as LK


def _src(**kw) -> dict:
    src = {"id": "f_L1_014", "type": "bathtub", "source": "from_documents", "type_method": "ai_two_pass",
           "footprint": {"center": [14.19, 19.71], "size": [2.07, 1.0], "rotation_deg": 0.0}}
    src.update(kw)
    return src


def _swapped(src: dict) -> tuple[dict, dict]:
    fin = copy.deepcopy(src)
    fin.update({"type": "shower", "shower_kind": "walk_in", "drawn_type": "bathtub",
                "drawn_footprint": copy.deepcopy(src["footprint"])})
    adj = {"by": "code", "stage": "layout", "rule": "infer.bath_or_shower", "reason": "UL200",
           "changed": {"type": "bathtub"}}
    fin["adjusted_by_ai"] = adj
    return fin, adj


def test_vision_typed_bathtub_may_become_a_walk_in_shower():
    src = _src()
    fin, adj = _swapped(src)
    assert LK.inferred_swap(src, fin, adj)


def test_code_inferred_bathtub_still_may_swap():
    src = _src(type_method="missing_member", inferred=True)
    fin, adj = _swapped(src)
    assert LK.inferred_swap(src, fin, adj)


def test_named_bathtub_keeps_its_type():
    for named in ({"type_method": "block"}, {"label": "KÜVET"}, {"type_raw": "bathtub_180"}):
        src = _src(**named)
        fin, adj = _swapped(src)
        assert not LK.inferred_swap(src, fin, adj), named


def test_swap_needs_the_drawn_type_and_a_code_record():
    src = _src()
    fin, adj = _swapped(src)
    fin["drawn_type"] = None
    assert not LK.inferred_swap(src, fin, adj)
    fin, adj = _swapped(src)
    adj["by"] = "agent"
    assert not LK.inferred_swap(src, fin, adj)
