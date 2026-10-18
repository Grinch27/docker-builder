#!/usr/bin/env python3
# Requirements: targets selects the sole Container builder; push validates and schedule monitors.
# Unknowns/research: deferred applications and external consumers require separate evidence.
# Optimization: select each Target once; diagnostics are shared across the selected builds.
# Risks/verification: reject ambiguous/duplicate targets; cover every configured platform without publication.
"""Plan Container builds and shared diagnostics from one public input."""

from __future__ import annotations

import json
import os
from pathlib import Path

import catalog


DIAGNOSTIC_IMAGES = ("debian:latest", "ubuntu:latest", "alpine:latest", "debian:sid", "ubuntu:devel")


def _target(config: dict, app: str, tag: str) -> dict:
    item = catalog.get(config, app, tag)
    target_id = app if tag == "latest" or app.endswith(("-" + tag, "_" + tag)) else app + "-" + tag
    return dict(item, target_id=target_id)


def _select(config: dict, text: str, all_targets: list[dict]) -> list[dict]:
    if not isinstance(text, str) or any(c in text for c in "\r\n\0"):
        raise ValueError("targets must be a single-line string")
    text = text.strip() or "vlmcsd"
    if text == "all":
        return list(all_targets)
    selected, seen = [], set()
    for token in text.split(","):
        parts = token.strip().split(":")
        if len(parts) not in {1, 2} or not parts[0] or parts[0] not in config["apps"]:
            raise ValueError("Unknown or malformed target: " + token)
        app = parts[0]
        if len(parts) == 1:
            targets = config["apps"][app]["targets"]
            if len(targets) != 1:
                raise ValueError("Tag required for multi-target application: " + app)
            tag = catalog.target_tag(targets[0])
        else:
            tag = parts[1]
        item = _target(config, app, tag)
        identity = (app, tag)
        if identity in seen:
            raise ValueError("Duplicate target: " + app + ":" + tag)
        seen.add(identity)
        selected.append(item)
    return selected


def plan(config: dict, event_name: str, inputs: dict) -> dict:
    """Select catalog-only matrices; no event or input can enable publication."""
    if event_name not in {"push", "schedule", "workflow_dispatch"}:
        raise ValueError("Core accepts push/schedule/workflow_dispatch only")
    if not isinstance(inputs, dict) or set(inputs) - {"targets"}:
        raise ValueError("Only targets input is supported")
    all_targets = [_target(config, app, catalog.target_tag(target))
                   for app, meta in config["apps"].items() for target in meta["targets"]]
    if not all_targets or len({t["target_id"] for t in all_targets}) != len(all_targets):
        raise ValueError("Empty or duplicated catalog target_id")
    manual = event_name == "workflow_dispatch"
    monitor = event_name == "schedule"
    selected = _select(config, inputs.get("targets", "vlmcsd"), all_targets) if manual else []
    if len(selected) > 256:
        raise ValueError("Container matrix exceeds GitHub's 256-job limit")
    versions = [dict(app_branch=app, tag_repo="latest") for app in config["apps"]] if monitor else []
    return {
        "build": str(manual).lower(), "monitor": str(monitor).lower(),
        "version_matrix": {"include": versions},
        "build_targets": {"include": selected},
        "images": list(DIAGNOSTIC_IMAGES),
        "image_platforms": [{"image_name": image, "arch": arch}
                            for image in DIAGNOSTIC_IMAGES for arch in ("amd64", "arm64")],
    }


def main() -> None:
    inputs = json.loads(os.environ.get("WORKFLOW_INPUTS", "{}"))
    result = plan(catalog.catalog_from_readme(Path("README.md")),
                  os.environ["GITHUB_EVENT_NAME"], inputs)
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        for key, value in result.items():
            text = json.dumps(value, separators=(",", ":")) if not isinstance(value, str) else value
            stream.write(key + "=" + text + "\n")
    print(json.dumps({key: result[key] for key in ("build", "monitor")} |
                     {"targets": len(result["build_targets"]["include"]),
                      "platforms": sum(len(t["arch_branch"].split(","))
                                       for t in result["build_targets"]["include"])}))


if __name__ == "__main__":
    main()
