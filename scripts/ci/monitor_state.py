#!/usr/bin/env python3
# Requirements: preserve README records and report monitor changes without selecting builds.
# Unknowns/research: external users of retired build-matrix artifacts must migrate.
# Optimization: remove build selection and force/custom-environment parameters from monitoring.
# Risks/verification: unchanged output fixtures, monitor-only edits and idempotence.
"""Build stable monitor outputs and README version sections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import catalog


README_FIELDS = [
    "app_branch",
    "tag_repo",
    "repo_dockerhub",
    "version",
    "base_image",
    "arch_branch",
    "platform_used",
    "status",
]

def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def normalize_record(item: dict[str, Any]) -> dict[str, str]:
    return {key: str(item.get(key, "")) for key in README_FIELDS}


def record_sort_key(item: dict[str, str]) -> tuple[str, str, str]:
    return (item.get("app_branch", ""), item.get("tag_repo", ""), item.get("repo_dockerhub", ""))


def load_version_artifacts(artifact_root: Path) -> list[dict[str, str]]:
    records = []
    for path in sorted(artifact_root.glob("version-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        records.append(normalize_record(data))
    return sorted(records, key=record_sort_key)


def parse_readme_versions(text: str) -> list[dict[str, str]]:
    # The combined v2 document is authoritative for the previous observation.
    document=catalog.validate_document(catalog.catalog_document_from_text(text))
    return sorted((normalize_record(r) for r in document['monitor']['records']),key=record_sort_key)


def render_readme(text: str, records: list[dict[str, str]]) -> str:
    document=catalog.validate_document(catalog.catalog_document_from_text(text))
    document['monitor']['records']=[dict(sorted(record.items())) for record in records]
    return catalog.replace_catalog_document(text,document)

def semantic_changed_apps(old_records: list[dict[str, str]], new_records: list[dict[str, str]]) -> list[str]:
    old_map = {
        (item["app_branch"], item["tag_repo"], item["repo_dockerhub"]): item
        for item in old_records
    }
    changed = []
    seen = set()
    for item in new_records:
        key = (item["app_branch"], item["tag_repo"], item["repo_dockerhub"])
        app = item["app_branch"]
        if old_map.get(key) != item and app not in seen:
            seen.add(app)
            changed.append(app)
    return sorted(changed)


def render_report(state: dict[str, Any]) -> str:
    lines = [
        "# Monitor Report",
        "",
        "This artifact is generated from semantic monitor state. Volatile run metadata is omitted.",
        "",
        f"- README changed: {str(state['readme_changed']).lower()}",
        f"- Changed apps: {len(state['changed_apps'])}",
        "",
        "## Changed Apps",
        "",
    ]
    if state["changed_apps"]:
        lines.extend(f"- `{app}`" for app in state["changed_apps"])
    else:
        lines.append("- None")

    return "\n".join(lines)


def write_outputs(output_dir: Path, state: dict[str, Any], report: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "monitor-state.json").write_text(dump_json(state), encoding="utf-8")
    (output_dir / "monitor-report.md").write_text(report, encoding="utf-8")
    (output_dir / "versions.json").write_text(dump_json(state["versions"]), encoding="utf-8")
    (output_dir / "changed-apps.json").write_text(dump_json(state["changed_apps"]), encoding="utf-8")
    (output_dir / "readme_changed.txt").write_text(
        "true" if state["readme_changed"] else "false", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", required=True)
    parser.add_argument("--readme-path", default="README.md")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    readme_path = Path(args.readme_path)
    original_readme = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
    old_records = parse_readme_versions(original_readme)
    new_records = load_version_artifacts(Path(args.artifact_root))

    changed_apps = semantic_changed_apps(old_records, new_records)

    rendered_readme = render_readme(original_readme, new_records)
    readme_changed = rendered_readme != original_readme
    if readme_changed:
        readme_path.write_text(rendered_readme, encoding="utf-8")

    state = {
        "changed_apps": changed_apps,
        "readme_changed": readme_changed,
        "schema_version": 1,
        "versions": new_records,
    }

    report = render_report(state)
    write_outputs(Path(args.output_dir), state, report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
