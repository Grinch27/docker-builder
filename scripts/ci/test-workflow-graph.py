#!/usr/bin/env python3
"""Guard the two-workflow GitHub Actions layout and reusable references."""
import re
from pathlib import Path

root = Path(__file__).resolve().parents[2]
flow = root / ".github" / "workflows"
files = {p.name for p in flow.glob("*.y*ml")}
expected = {"gpt_dev.yml", "download_artifact.yml"}
assert files == expected, f"Unexpected workflows: {sorted(files)} (expected {sorted(expected)})"
for path in flow.glob("*.y*ml"):
    contents = path.read_text(encoding="utf-8")
    for ref in re.findall(r'uses:\s+\./\.github/workflows/([a-zA-Z0-9_.-]+\.yml)', contents):
        assert ref in expected, f"Dangling reusable workflow reference: {path.name} -> {ref}"
print("Workflow dependency guard: PASS (2 workflows)")
