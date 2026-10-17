#!/usr/bin/env python3
# Requirements/ambiguities: legacy external callers must migrate to docker_allinone.yml.
# Research/optimization: ordinary staging pushes validate only; explicit verification keeps representative coverage.
# Risks: production/container/Dev may publish; staging acceptance must force publication off.
# Verification: explicit selector parsing, full catalog coverage, Dev/Container selection and event isolation.
"""Plan the single workflow without executing builds, probes, or external writes."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import catalog


ROUTES = {"validate", "production", "monitor", "build", "test", "smoke", "dev",
          "diagnostics", "container", "registry-smoke"}
DEV_MODES = {"preflight", "auto", "build", "promote-dockerhub", "promote-ghcr", "promote-all"}
# This is the former Dev auto-selection policy, not another application catalog.
DEV_EXCLUDED = {"baidunetdisk", "cloudflare-warp", "expressvpn", "ffmpeg", "novnc",
                "protonvpn", "sdnext", "sdnext-dev", "stable-diffusion-webui-amdgpu",
                "steamcmd", "ttrss"}
PROBE_APPS = {"aria2", "curl", "privoxy", "squid", "dnscrypt-proxy", "doh-nosni"}


def target_id(app: str, tag: str) -> str:
    if tag == "latest" or app.endswith(("-" + tag, "_" + tag)):
        return app
    return app + "-" + tag


def plan(config: dict, event_name: str, event: dict, inputs: dict, runner: str) -> dict:
    """Reject ambiguous/unsafe selections before returning any Job outputs."""
    payload = event.get("client_payload", {}) if event_name == "repository_dispatch" else {}

    def value(key: str, default: str = "") -> str:
        raw = inputs.get(key) or payload.get(key) or default
        if isinstance(raw, bool):
            raw = str(raw).lower()
        if not isinstance(raw, str) or any(c in raw for c in "\r\n\0"):
            raise ValueError("Expected a single-line string for " + key)
        return raw

    route = value("execution_route", "production")
    app, tag = value("app_branch"), value("tag_repo")
    selected_id = value("target_id")
    probe = False
    if event_name in {"push", "pull_request"}:
        # User-controlled push messages can select read-only tests, never publication.
        route, app, tag, selected_id = "validate", "", "", ""
        message = event.get("head_commit", {}).get("message", "") if event_name == "push" else ""
        if "[full-retest:" in message:
            match = re.search(r"\[full-retest:([a-z0-9_.-]+):([a-z0-9_.-]+)\]", message)
            if not match:
                raise ValueError("Malformed full-retest selector")
            route, app, tag = "test", *match.groups()
        elif "[full-build]" in message:
            route = "test"
        elif "[smoke-target:" in message:
            match = re.search(r"\[smoke-target:([a-zA-Z0-9_.-]+)\]", message)
            if not match:
                raise ValueError("Malformed smoke-target selector")
            route, selected_id = "smoke", match.group(1)
        elif "[smoke-vlmcsd]" in message:
            route, app = "test", "vlmcsd"
        elif "[probe-smoke]" in message:
            route, probe = "test", True
        elif message.startswith("ci: smoke catalog build"):
            route = "registry-smoke"
        elif "[diagnostics-full]" in message:
            route = "diagnostics"
    elif event_name == "schedule":
        route = "production"
    elif event_name not in {"workflow_dispatch", "workflow_call", "repository_dispatch"}:
        raise ValueError("Unsupported event: " + event_name)
    if route not in ROUTES:
        raise ValueError("Unknown execution_route: " + route)
    dev_mode = value("dev_mode", "preflight")
    if dev_mode not in DEV_MODES:
        raise ValueError("Unknown dev_mode: " + dev_mode)
    force = value("force_build", "false").lower()
    if force not in {"true", "false"}:
        raise ValueError("force_build must be true or false")
    diagnostic_mode = value("diagnostic_mode", "both")
    if diagnostic_mode not in {"version", "layers", "both", "all-platforms"}:
        raise ValueError("Unknown diagnostic_mode")
    profile = value("layer_profile", "stable")
    if profile not in {"stable", "base"}:
        raise ValueError("Unknown layer_profile")

    all_targets = [dict(catalog.get(config, name, t["tag"]),
                        target_id=target_id(name, t["tag"]), custom_env="", runner_image=runner)
                   for name, meta in config["apps"].items() for t in meta["targets"]]
    if len({t["target_id"] for t in all_targets}) != len(all_targets):
        raise ValueError("Duplicate target_id in catalog")
    targets = all_targets
    if app:
        targets = [t for t in targets if t["app_branch"] == app]
    if tag:
        targets = [t for t in targets if t["tag_repo"] == tag]
    if selected_id:
        targets = [t for t in targets if t["target_id"] == selected_id]
    custom = value("custom_env")
    raw_matrix = inputs.get("build_matrix") or payload.get("build_matrix") or ""
    if not isinstance(raw_matrix, str):
        raise ValueError("build_matrix must be JSON text")
    if custom and route in {"test", "smoke", "dev"}:
        raise ValueError("This route uses catalog settings; custom_env is unsupported")
    if raw_matrix:
        if route not in {"production", "monitor", "build", "test", "container"} or app or tag or selected_id:
            raise ValueError("build_matrix cannot be combined with other target selectors or this route")
        raw = json.loads(raw_matrix)
        rows = raw.get("include") if isinstance(raw, dict) else raw
        if not isinstance(rows, list) or not rows:
            raise ValueError("build_matrix must contain a non-empty target list")
        targets = []
        for row in rows:
            if not isinstance(row, dict) or set(row) - {"app_branch", "tag_repo", "custom_env"}:
                raise ValueError("Matrix entries accept app_branch, tag_repo, custom_env only")
            selected = [t for t in all_targets if t["app_branch"] == row.get("app_branch")
                        and t["tag_repo"] == row.get("tag_repo", "latest")]
            if len(selected) != 1:
                raise ValueError("Matrix target is not in the README catalog")
            override = row.get("custom_env", custom)
            if not isinstance(override, str) or any(c in override for c in "\r\n\0"):
                raise ValueError("Invalid matrix custom_env")
            targets.append(dict(selected[0], custom_env=override))
    else:
        targets = [dict(t, custom_env=custom) for t in targets]
    if not targets or len({t["target_id"] for t in targets}) != len(targets):
        raise ValueError("Empty or duplicated target selection")
    if route == "container" and len(targets) != 1:
        raise ValueError("container requires exactly one configured target")
    if route == "smoke" and len(targets) != 1:
        raise ValueError("smoke requires exactly one configured target")
    if route == "dev" and dev_mode.startswith("promote-"):
        if len(targets) != 1 or not value("version") or not value("revision"):
            raise ValueError("Promotion requires one target, version and revision")

    test_matrix = [{"app": t["app_branch"], "tag": t["tag_repo"], "platform": platform}
                   for t in targets for platform in t["arch_branch"].split(",")
                   if not probe or (t["app_branch"] in PROBE_APPS and platform in {"linux/amd64", "linux/arm64"})]
    platform = value("platform")
    if platform:
        if route != "test":
            raise ValueError("platform only applies to test Jobs")
        test_matrix = [t for t in test_matrix if t["platform"] == platform]
        if not test_matrix:
            raise ValueError("platform does not match selected configured targets")
    if len(test_matrix) > 256:
        raise ValueError("Test matrix exceeds GitHub's 256-job limit")
    dev_targets = targets
    if not (app or tag or selected_id) and route == "dev":
        dev_targets = [t for t in targets if t["app_branch"] not in DEV_EXCLUDED]
    # Preserve the former Dev-only destination; production catalog tags stay unchanged.
    if route == "dev":
        dev_targets = [dict(t, tag_repo="alpine") if t["app_branch"] == "novnc_alpine" else t
                       for t in dev_targets]
    versions = []
    for name in dict.fromkeys(t["app_branch"] for t in targets):
        versions.append(dict(app_branch=name, tag_repo=tag or "latest", custom_env=custom, runner_image=runner))
    if route == "diagnostics":
        chosen_app = app or "vlmcsd"
        versions = [dict(app_branch=chosen_app, tag_repo=tag or "latest", custom_env=custom, runner_image=runner)]
    image = value("image_name")
    if image and not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9./_:@-]*", image):
        raise ValueError("Invalid diagnostic image reference")
    images = ([image] if image else
              ["ubuntu:latest", "debian:latest", "alpine:latest"] if profile == "base" else
              ["debian:latest", "ubuntu:latest", "alpine:latest", "debian:sid", "ubuntu:devel"])
    return {
        "route": route, "dev_mode": "smoke-target" if route == "smoke" else dev_mode,
        "target_id": targets[0]["target_id"] if len(targets) == 1 else "",
        "force_build": force, "publish": str(route == "production").lower(),
        "may_publish": str(route in {"production", "container"} or
                           (route == "dev" and dev_mode != "preflight")).lower(),
        "version": value("version"), "revision": value("revision"), "custom_env": custom,
        "fetch_versions": str(route in {"production", "monitor", "build"} or
                              (route == "diagnostics" and diagnostic_mode in {"version", "both"})).lower(),
        "diagnostic_mode": diagnostic_mode, "probe": str(probe).lower(),
        "version_matrix": {"include": versions}, "build_targets": {"include": targets},
        "dev_matrix": {"include": dev_targets}, "test_matrix": {"include": test_matrix},
        "images": images, "image_platforms": [{"image_name": image, "arch": arch}
                                                  for image in images for arch in ["amd64", "arm64"]],
    }


def staging_plan(config: dict, event_name: str, event: dict, inputs: dict, runner: str) -> dict:
    """Plan only nonpublishing routes for the explicitly isolated gpt_dev.yml."""
    selected = dict(inputs)
    route = selected.get("execution_route") or "verification"
    if event_name == "push":
        route = "validate"
        message = event.get("head_commit", {}).get("message", "")
        selectors = re.findall(r"\[gpt-[^\]]*\]", message)
        if message.count("[gpt-") != len(selectors):
            raise ValueError("Unterminated staging selector")
        if len(selectors) > 1:
            raise ValueError("Use exactly one staging selector per push")
        selector = selectors[0] if selectors else ""
        if selector in {"[gpt-verification]", "[gpt-validate]", "[gpt-acceptance]"}:
            route = selector[len("[gpt-"):-1]
        elif selector.startswith("[gpt-retest:"):
            match = re.fullmatch(r"\[gpt-retest:([^\]]+)\]", selector)
            pairs = match.group(1).split(",") if match else []
            if not pairs or any(not re.fullmatch(r"[a-z0-9_.-]+:[a-z0-9_.-]+", pair) for pair in pairs):
                raise ValueError("Malformed staging retest selector")
            selected["build_matrix"] = json.dumps({"include": [
                dict(zip(("app_branch", "tag_repo"), pair.split(":"))) for pair in pairs]})
            route = "test"
        patterns = [(r"\[gpt-dev:([a-z0-9_.-]+):([a-z0-9_.-]+)\]", "dev-verify"),
                    (r"\[gpt-container:([a-z0-9_.-]+):([a-z0-9_.-]+)\]", "container-verify"),
                    (r"\[gpt-build:([a-z0-9_.-]+):([a-z0-9_.-]+)\]", "build"),
                    (r"\[gpt-monitor:([a-z0-9_.-]+):([a-z0-9_.-]+)\]", "monitor"),
                    (r"\[gpt-smoke:([a-zA-Z0-9_.-]+)\]", "smoke")]
        for pattern, candidate in patterns:
            match = re.fullmatch(pattern, selector)
            if match:
                route = candidate
                if route == "smoke":
                    selected["target_id"] = match.group(1)
                else:
                    selected["app_branch"], selected["tag_repo"] = match.groups()
                break
        if selector and route == "validate" and selector != "[gpt-validate]":
            raise ValueError("Unknown or malformed staging selector")
    elif event_name != "workflow_dispatch":
        raise ValueError("Staging accepts push/workflow_dispatch only")
    if route not in {"verification", "acceptance", "dev-verify", "container-verify",
                     "validate", "monitor", "build", "test", "smoke",
                     "diagnostics", "registry-smoke", "dev"}:
        raise ValueError("Publishing routes are prohibited in gpt_dev.yml")
    if route == "dev" and selected.get("dev_mode", "preflight") != "preflight":
        raise ValueError("Dev build/promotion is prohibited in gpt_dev.yml")
    acceptance_routes = {"acceptance", "dev-verify", "container-verify"}
    if route in {"dev-verify", "container-verify"} and any(
            selected.get(key) for key in ("platform", "custom_env", "build_matrix")):
        raise ValueError("Dev/Container acceptance uses one unmodified catalog target")
    if route == "acceptance" and any(selected.get(key) for key in
                                     ("app_branch", "tag_repo", "target_id", "build_matrix", "platform", "custom_env")):
        raise ValueError("Full acceptance cannot be combined with target filters")
    if route in {"dev-verify", "container-verify"} and not any(
            selected.get(key) for key in ("app_branch", "target_id", "build_matrix")):
        selected.update(app_branch="vlmcsd", tag_repo="latest")
    selected["execution_route"] = "test" if route in acceptance_routes | {"verification"} else route
    result = plan(config, "workflow_dispatch", {}, selected, runner)
    if route in acceptance_routes:
        if route == "acceptance":
            target = next(t for t in result["build_targets"]["include"]
                          if t["app_branch"] == "vlmcsd" and t["tag_repo"] == "latest")
        else:
            if len(result["build_targets"]["include"]) != 1:
                raise ValueError("Dev/Container acceptance requires exactly one configured target")
            target = result["build_targets"]["include"][0]
        dev = plan(config, "workflow_dispatch", {},
                   dict(execution_route="dev", dev_mode="build", target_id=target["target_id"]), runner)
        result.update(dev_mode="build", target_id=target["target_id"],
                      dev_matrix=dev["dev_matrix"], build_targets={"include": [target]},
                      force_build="true", fetch_versions="false")
    if route == "build" and len(result["build_targets"]["include"]) != 1:
        raise ValueError("Staged build requires exactly one configured target")
    if route in {"verification", "build"}:
        result["force_build"] = "true"
    if route == "verification":
        samples = {("aria2", "latest"), ("samba", "alpine"),
                   ("vlmcsd", "latest"), ("runner", "actions-slim")}
        result["test_matrix"]["include"] = [t for t in result["test_matrix"]["include"]
                                             if (t["app"], t["tag"]) in samples]
        actual = {(t["app"], t["tag"]) for t in result["test_matrix"]["include"]}
        if actual != samples:
            raise ValueError("Configured representative test target missing")
        result["build_targets"]["include"] = [t for t in result["build_targets"]["include"]
                                               if t["app_branch"] == "vlmcsd"]
        result["version_matrix"]["include"] = [dict(app_branch="vlmcsd", tag_repo="latest",
                                                      custom_env="", runner_image=runner)]
        result["fetch_versions"] = "true"
        result["diagnostic_mode"] = "both"
        result["images"] = ["alpine:latest"]
        result["image_platforms"] = [dict(image_name="alpine:latest", arch=arch)
                                     for arch in ["amd64", "arm64"]]
    result.update(route=route, publish="false", may_publish="false")
    return result


def main() -> None:
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text(encoding="utf-8"))
    inputs = json.loads(os.environ.get("WORKFLOW_INPUTS", "{}"))
    planner = staging_plan if os.environ.get("WORKFLOW_READ_ONLY") == "true" else plan
    result = planner(catalog.catalog_from_readme(Path("README.md")),
                  os.environ["GITHUB_EVENT_NAME"], event, inputs, os.environ["RUNNER_IMAGE"])
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
        for key, value in result.items():
            text = json.dumps(value, separators=(",", ":")) if not isinstance(value, str) else value
            stream.write(key + "=" + text + "\n")
    print(json.dumps({"route": result["route"], "targets": len(result["build_targets"]["include"]),
                      "tests": len(result["test_matrix"]["include"]),
                      "standard_publish": result["publish"], "may_publish": result["may_publish"]}))


if __name__ == "__main__":
    main()
