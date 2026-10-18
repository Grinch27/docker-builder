#!/usr/bin/env python3
# Requirements: expose only targets/verify; push validates, schedule monitors, dispatch never publishes.
# Unknowns/research: external callers must migrate retired routes and commit selectors explicitly.
# Optimization: one catalog selector and event flags replace overlapping route/matrix/profile parsers.
# Risks/verification: reject ambiguous/duplicate targets and false-like values; retain full platform coverage.
"""Plan fixed nonpublishing Jobs from the event and two public inputs."""

from __future__ import annotations

import json
import os
from pathlib import Path

import catalog


DIAGNOSTIC_IMAGES = ("debian:latest", "ubuntu:latest", "alpine:latest", "debian:sid", "ubuntu:devel")


def _target(config: dict, app: str, tag: str, runner: str) -> dict:
    item = catalog.get(config, app, tag)
    target_id = app if tag == "latest" or app.endswith(("-" + tag, "_" + tag)) else app + "-" + tag
    return dict(item, target_id=target_id, custom_env="", runner_image=runner)


def _verify(value) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value in {"true", "false"}:
        return value == "true"
    raise ValueError("verify must be a boolean or true/false string")


def _select(config: dict, text: str, all_targets: list[dict], runner: str) -> list[dict]:
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
        item = _target(config, app, tag, runner)
        identity = (app, tag)
        if identity in seen:
            raise ValueError("Duplicate target: " + app + ":" + tag)
        seen.add(identity)
        selected.append(item)
    return selected


def plan(config: dict, event_name: str, event: dict, inputs: dict, runner: str) -> dict:
    """Select catalog-only matrices; no event or input can enable publication."""
    if event_name not in {"push", "schedule", "workflow_dispatch"}:
        raise ValueError("Core accepts push/schedule/workflow_dispatch only")
    if not isinstance(inputs, dict) or set(inputs) - {"targets", "verify"}:
        raise ValueError("Only targets and verify inputs are supported")
    if event_name == "push" and "[gpt-" in (event.get("head_commit") or {}).get("message", ""):
        raise ValueError("Commit selectors are retired; use workflow_dispatch targets/verify")
    all_targets = [_target(config, app, catalog.target_tag(target), runner)
                   for app, meta in config["apps"].items() for target in meta["targets"]]
    if not all_targets or len({t["target_id"] for t in all_targets}) != len(all_targets):
        raise ValueError("Empty or duplicated catalog target_id")
    manual = event_name == "workflow_dispatch"
    verify = manual and _verify(inputs.get("verify", False))
    monitor = event_name == "schedule" or (manual and not verify)
    selected = (_select(config, inputs.get("targets", "vlmcsd"), all_targets, runner)
                if manual else all_targets)
    if manual and not verify and (len(selected) != 1 or inputs.get("targets", "").strip() == "all"):
        raise ValueError("Multiple targets or all require verify=true")
    representative = None
    if verify:
        representative = selected[0] if len(selected) == 1 else _target(config, "vlmcsd", "latest", runner)
    test_matrix = [{"app": t["app_branch"], "tag": t["build_tag"], "platform": platform}
                   for t in selected for platform in t["arch_branch"].split(",")] if verify else []
    if len(test_matrix) > 256:
        raise ValueError("Test matrix exceeds GitHub's 256-job limit")
    # novnc_alpine keeps its historical Dev destination; Container uses its configured latest tag.
    dev_target = (dict(representative, tag_repo="alpine") if representative and
                  representative["app_branch"] == "novnc_alpine" else representative)
    version_targets = [representative] if verify else selected
    versions = [dict(app_branch=t["app_branch"], tag_repo="latest" if event_name == "schedule" else t["build_tag"],
                     custom_env="", runner_image=runner)
                for t in {t["app_branch"]: t for t in version_targets}.values()]
    return {
        "build": str(manual and not verify).lower(), "verify": str(verify).lower(),
        "monitor": str(monitor).lower(), "fetch_versions": str(monitor or verify).lower(),
        "force_build": str(manual).lower(), "publish": "false", "may_publish": "false",
        "version_matrix": {"include": versions},
        "build_targets": {"include": [representative] if verify else selected},
        "dev_matrix": {"include": [dev_target] if verify else []},
        "test_matrix": {"include": test_matrix},
        "images": list(DIAGNOSTIC_IMAGES),
        "image_platforms": [{"image_name": image, "arch": arch}
                            for image in DIAGNOSTIC_IMAGES for arch in ("amd64", "arm64")],
    }


def main() -> None:
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    inputs = json.loads(os.environ.get("WORKFLOW_INPUTS", "{}"))
    result = plan(catalog.catalog_from_readme(Path("README.md")),
                  os.environ["GITHUB_EVENT_NAME"], event, inputs, os.environ["RUNNER_IMAGE"])
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        for key, value in result.items():
            text = json.dumps(value, separators=(",", ":")) if not isinstance(value, str) else value
            stream.write(key + "=" + text + "\n")
    print(json.dumps({key: result[key] for key in ("build", "verify", "monitor", "publish", "may_publish")} |
                     {"targets": len(result["build_targets"]["include"]),
                      "tests": len(result["test_matrix"]["include"])}))


if __name__ == "__main__":
    main()
