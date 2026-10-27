"""27 Oct 2026 (user: "all the solutions must be general. check the project, all the decisions and solutions must be
general not project specific"; CLAUDE.md, 26 Oct 2026: "Every fix is general: a rule of the pipeline for every
project; the project that showed the problem is only the test case"). The pipeline's code never names a project or an
element id of one house in a string it computes with: a rule that names ``real06`` or ``f_L1_011`` serves one house.
Comments and docstrings may name the project where a problem was first seen (provenance). The experiment and job
lists that choose which projects a run, an A/B test or a bake-off takes, the pod self-check's scripted answers and the
synthetic projects' generator name projects on purpose (``ALLOWED``)."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECIFIC = re.compile(r"\b(real0\d|synthetic-0\d|deneme1|r_L-?\d_[a-z]|f_L-?\d_\d|d_L-?\d_\d|w_L-?\d_\d|"
                      r"win_L-?\d_\d|o_L-?\d_\d|os_L-?\d_|sa_L-?\d_|sd_L-?\d_\d|sv_L-?\d_)", re.I)
ALLOWED = {"wenart/run/ab.py", "wenart/run/prep.py", "wenart/agent/bakeoff.py", "wenart/assets/audit/demands.py",
           "wenart/agent/podcheck.py"}
ALLOWED_DIRS = ("wenart/synthetic/",)


def _docstrings(tree) -> set:
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant):
                out.add(id(first.value))
    return out


def test_no_pipeline_code_names_a_project_or_an_element_of_one_house():
    hits = []
    for path in sorted((ROOT / "wenart").rglob("*.py")) + sorted((ROOT / "scripts").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWED or rel.startswith(ALLOWED_DIRS):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        docs = _docstrings(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
                m = SPECIFIC.search(node.value)
                if m:
                    hits.append(f"{rel}:{node.lineno}: {m.group(0)!r} in {node.value[:80]!r}")
    assert not hits, "project-specific strings in pipeline code (make the rule general):\n" + "\n".join(hits)
