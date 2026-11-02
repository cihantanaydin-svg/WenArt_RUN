"""2 Nov 2026 (user: "start with the score-budget table"): what each family of findings and each judge tag costs the
house score (``wenart.agent.judge.score_budget``). CPU only."""
from wenart.agent import judge as JD


def test_budget_ranks_families_and_tags_by_their_gain():
    rows = [{"view": "v1", "client_ready_score": 2, "tags": ["empty_room", "bare_material"], "note": "an empty shell"},
            {"view": "v2", "client_ready_score": 4, "tags": ["looks_acceptable"], "note": "fine"},
            {"view": "v3", "client_ready_score": 1, "tags": ["empty_room"], "note": "a grey box"}]
    code = [{"source": "code", "check": "F7", "severity": "critical", "target": "f1", "message": "basin blocks door"}]
    model = [{"line": "inspector", "check": "D3", "severity": "major", "target": f"f{k}", "message": "odd wood"}
             for k in range(4)]
    b = JD.score_budget(rows, code, model, 2, views=3)
    base = JD.house_score(rows, code, model, 2, views=3)["score"]
    assert b["score"]["score"] == base
    fam = {r["family"]: r for r in b["families"]}
    assert fam["code:F7"]["critical"] == 1 and fam["inspector:D3"]["major"] == 4
    assert fam["code:F7"]["gain"] == round(JD.house_score(rows, [], model, 2, views=3)["score"] - base, 2)
    assert "architect:open major points" in fam and all(r["gain"] > 0 for r in b["families"])
    assert [r["gain"] for r in b["families"]] == sorted((r["gain"] for r in b["families"]), reverse=True)
    tags = {r["tag"]: r for r in b["tags"]}
    assert tags["empty_room"]["views"] == 2 and tags["empty_room"]["gain"] > tags["bare_material"]["gain"] > 0
    assert "looks_acceptable" not in tags
    assert [v["view"] for v in b["views"]] == ["v3", "v1"]
    md = JD.budget_md(b)
    assert "| code:F7 | 1 | 0 |" in md and "## The judge's tags" in md and "Views below 3" in md
