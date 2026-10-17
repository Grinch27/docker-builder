#!/usr/bin/env python3
"""Read-only guard for obsolete CI workflow paths and live reusable dependencies."""
import re
from pathlib import Path

root=Path(__file__).resolve().parents[2]
flow=root/".github"/"workflows"
files={p.name for p in flow.glob("*.yml")} - {"gpt_dev.yml"}
protected={"docker_allinone.yml","docker_allinone_dev.yml","docker_allinone_gpt.yml",
           "monitor-images.yml","call-build_dev.yml",
           "pull_artifact-dev.yml","download_artifact.yml"}
removed={"baseimage_dev.yml","call-fetch_stable.yml","call-fetch_dev.yml"}
missing=protected-files
assert not missing, f"Protected workflows missing: {sorted(missing)}"
assert not (removed&files), f"Retired workflow still present: {removed&files}"
assert "diagnostics.yml" in files
for p in flow.glob("*.yml"):
    text=p.read_text(encoding="utf-8")
    for ref in re.findall(r'uses:\s+\./\.github/workflows/([a-zA-Z0-9_.-]+\.yml)',text):
        assert ref in files, f"Dangling reusable workflow reference: {p.name} -> {ref}"
assert len(files)==14, f"Unexpected workflow count: {len(files)}"
print(f"Workflow dependency guard: PASS ({len(files)} workflows)")

