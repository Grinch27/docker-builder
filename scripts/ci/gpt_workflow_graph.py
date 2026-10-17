#!/usr/bin/env python3
# Requirements: core capabilities belong to ordinary Jobs in docker_allinone.yml.
# Unknowns/research: external callers of retired paths need migration, not silent redirects.
# Risks/verification: missing needs, dependency cycles and nested workflow references.
# Optimization: standard-library guard; actionlint separately validates the full YAML schema.
"""Check the core workflow Job graph without adding a CI dependency."""
import re
from pathlib import Path

def job_blocks(text):
    body = text.split("\njobs:\n", 1)[1]
    matches = list(re.finditer(r"^  ([a-zA-Z0-9_-]+):\s*$", body, re.MULTILINE))
    return {m[1]: body[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(body)]
            for i, m in enumerate(matches)}


def dependencies(block):
    single = re.search(r"^    needs: ([a-zA-Z0-9_-]+)$", block, re.MULTILINE)
    if single:
        return {single[1]}
    multiple = re.search(r"^    needs:\n((?:    - [a-zA-Z0-9_-]+\n)+)", block, re.MULTILINE)
    return set(re.findall(r"    - ([a-zA-Z0-9_-]+)", multiple[1])) if multiple else set()


def validate(root):
    flow = root / ".github/workflows"
    files = {p.name for p in flow.glob("*.y*ml")}
    utilities = {"pull_artifact-dev.yml", "download_artifact.yml"}
    assert utilities <= files, "Independent Artifact utilities missing"
    assert "gpt_dev.yml" in files, "Staging workflow missing"
    text = (flow / "gpt_dev.yml").read_text(encoding="utf-8")
    blocks = job_blocks(text)
    required = {"runner-image", "validate", "plan", "fetch-versions", "monitor", "check", "build",
                "dev-inspect", "dev-build", "smoke", "test-images", "registry-smoke",
                "diagnostic-layers", "diagnostic-platforms", "diagnostic-collect",
                "diagnostic-meta-platforms", "diagnostic-validate", "container-build"}
    assert required <= blocks.keys(), "Core capability Job missing"
    edges = {key: dependencies(block) for key, block in blocks.items()}
    for key, block in blocks.items():
        assert not re.search(r"^    uses:", block, re.MULTILINE), "Nested workflow remains: " + key
        assert edges[key] <= blocks.keys(), "Dangling needs for " + key
        references = set(re.findall(r"needs\.([a-zA-Z0-9_-]+)\.", block))
        assert references <= edges[key], "Undeclared needs for " + key + ": " + str(references - edges[key])
    visiting, visited = set(), set()

    def visit(key):
        assert key not in visiting, "Job dependency cycle: " + key
        if key in visited:
            return
        visiting.add(key)
        for parent in edges[key]:
            visit(parent)
        visiting.remove(key)
        visited.add(key)

    for key in blocks:
        visit(key)
    print(f"GPT candidate Job graph: PASS ({len(blocks)} Jobs, {len(utilities)} independent utilities)")


if __name__ == "__main__":
    validate(Path(__file__).resolve().parents[2])

