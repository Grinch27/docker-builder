#!/usr/bin/env python3
# Requirements: share the Container builder across daily, manual and AdGuard release runs.
# Unknowns/research: qualify deferred Targets independently before adding them to the daily list.
# Optimization: select each Target once and share the fixed OCI diagnostics across the build matrix.
# Risks/verification: use the same daily matrix for schedule and dispatch and reject shared Docker Hub destinations.
"""Plan Container builds and shared diagnostics from one public input."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess

import catalog


DIAGNOSTIC_IMAGES = ("debian:latest", "ubuntu:latest", "alpine:latest", "debian:sid", "ubuntu:devel")
DAILY_TARGETS = (
    "adguardvpn-cli:release",
    "adguardvpn-cli:beta",
    "adguardvpn-cli:nightly",
    "aria2",
    "baidunetdisk:dev",
    "cloudflare-warp",
    "curl",
    "dnscrypt-proxy",
    "doh-nosni",
    "nordvpn",
    "novnc",
    "novnc_alpine",
    "openwrt:main",
    "privoxy",
    "protonvpn",
    "runner:actions",
    "runner:actions-slim",
    "runner:dev",
    "runner:slim",
    "samba:alpine",
    "samba:latest",
    "squid",
    "steamcmd:dev",
    "vlmcsd",
)
ADGUARD_RELEASE = ("adguardvpn-cli", "release")
ADGUARD_RELEASE_PATHS = ("application/adguardvpn-cli/.dockerignore",
                        "application/adguardvpn-cli/release.Dockerfile")
DAILY_RELEASE_PATHS = (
    ".github/workflows/gpt_dev.yml",
    "scripts/ci/build-image.sh",
    "scripts/ci/catalog.py",
    "scripts/ci/compare_image_snapshot.py",
    "scripts/ci/materialize_test_hooks.py",
    "scripts/ci/publish-accepted-image.sh",
    "scripts/ci/verify_image_archive.py",
    "scripts/ci/workflow_plan.py",
)


def _adguard_release_inputs(source: str) -> tuple:
    app, tag = ADGUARD_RELEASE
    return (catalog.get(catalog.catalog_data_from_text(source), app, tag),
            catalog.embedded_meta_from_text(source).get(app),
            catalog.embedded_tests_from_text(source)[app])


def changed_push_targets(before: str, readme: Path) -> str | None:
    """Verify the daily matrix after shared changes and the release target after its own changes."""
    if not re.fullmatch(r"[0-9a-f]{40}", before):
        raise ValueError("Expected a push base commit SHA")
    if before == "0" * 40:
        return "daily"
    changed = set(subprocess.check_output(
        ["git", "diff", "--name-only", before, "HEAD", "--",
         *DAILY_RELEASE_PATHS, *ADGUARD_RELEASE_PATHS, "README.md"],
        text=True,
    ).splitlines())
    if changed.intersection(DAILY_RELEASE_PATHS):
        return "daily"
    if changed.intersection(ADGUARD_RELEASE_PATHS):
        return ":".join(ADGUARD_RELEASE)
    if "README.md" in changed:
        previous = subprocess.check_output(["git", "show", f"{before}:README.md"], text=True)
        if _adguard_release_inputs(previous) != _adguard_release_inputs(readme.read_text(encoding="utf-8")):
            return ":".join(ADGUARD_RELEASE)
    return None


def _select(config: dict, text: str, all_targets: list[dict]) -> list[dict]:
    if not isinstance(text, str) or any(c in text for c in "\r\n\0"):
        raise ValueError("targets must be a single-line string")
    text = text.strip() or "vlmcsd"
    if text == "all":
        return list(all_targets)
    if text == "daily":
        text = ",".join(DAILY_TARGETS)
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
        item = catalog.get(config, app, tag)
        identity = (app, tag)
        if identity in seen:
            raise ValueError("Duplicate target: " + app + ":" + tag)
        seen.add(identity)
        selected.append(item)
    return selected


def plan(config: dict, event_name: str, inputs: dict, *, push_targets: str | None = None) -> dict:
    """Plan daily monitoring/builds, manual builds and automatic release pushes."""
    if event_name not in {"push", "schedule", "workflow_dispatch"}:
        raise ValueError("Core accepts push/schedule/workflow_dispatch only")
    if not isinstance(inputs, dict) or set(inputs) - {"targets"}:
        raise ValueError("Only targets input is supported")
    all_targets = [catalog.get(config, app, catalog.target_tag(target))
                   for app, meta in config["apps"].items() for target in meta["targets"]]
    if not all_targets:
        raise ValueError("Empty catalog")
    manual = event_name == "workflow_dispatch"
    monitor = event_name == "schedule"
    selected = []
    if manual or monitor:
        selected = _select(config, "daily" if monitor else inputs.get("targets", "vlmcsd"), all_targets)
    elif push_targets is not None:
        selected = _select(config, push_targets, all_targets)
    for release in selected:
        if (release["app_branch"], release["build_tag"]) != ADGUARD_RELEASE:
            continue
        if (release["repo_dockerhub"] != "grinch27/adguardvpn-cli" or
                release["publish_tag"] != "release" or
                set(release["arch_branch"].split(",")) != {"linux/amd64", "linux/arm64"} or
                release["build_arg"] != "update_channel=release"):
            raise ValueError("AdGuard Docker Hub destination, platforms or channel changed")
    if len(selected) > 256:
        raise ValueError("Container matrix exceeds GitHub's 256-job limit")
    destinations = {(row["repo_dockerhub"], row["publish_tag"]) for row in selected}
    if len(destinations) != len(selected):
        raise ValueError("Selected targets share a Docker Hub destination")
    versions = [dict(app_branch=app, tag_repo="latest") for app in config["apps"]] if monitor else []
    return {
        "build": str(bool(selected)).lower(), "monitor": str(monitor).lower(),
        "version_matrix": {"include": versions},
        "build_targets": {"include": selected},
        "images": list(DIAGNOSTIC_IMAGES),
        "image_platforms": [{"image_name": image, "arch": arch}
                            for image in DIAGNOSTIC_IMAGES for arch in ("amd64", "arm64")],
    }


def main() -> None:
    inputs = json.loads(os.environ.get("WORKFLOW_INPUTS", "{}"))
    readme = Path("README.md")
    event = os.environ["GITHUB_EVENT_NAME"]
    push_targets = None
    if (event == "push" and os.environ.get("GITHUB_REF") == "refs/heads/main"
            and os.environ.get("GITHUB_REPOSITORY") == "Grinch27/docker-builder"):
        push_targets = changed_push_targets(os.environ["PUSH_BEFORE"], readme)
    result = plan(catalog.catalog_from_readme(readme), event, inputs,
                  push_targets=push_targets)
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
