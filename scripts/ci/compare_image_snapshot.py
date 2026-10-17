#!/usr/bin/env python3
# Requirements: preserve the shared Dev/smoke OCI comparison schema and UNKNOWN failure boundary.
# Unknowns/research: live publication and deferred application failures remain separate work.
# Optimization: maintain the previously identical comparison algorithm once, without registry or Docker access.
# Risks: malformed input must fail; missing/unobservable registry evidence must retain its existing meaning.
# Verification: CLI fixtures, platform/config/version changes, unknown evidence and extraction parity.
"""Compare BASELINE CANDIDATE PLATFORM MODE OUTPUT using saved JSON evidence only."""

import json
import sys
from pathlib import Path


def main():
    baseline_path, candidate_path, platform, mode, out_path = sys.argv[1:]
    baseline = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    candidate = json.loads(Path(candidate_path).read_text(encoding="utf-8"))

    config_fields = (
        "Env",
        "Entrypoint",
        "Cmd",
        "User",
        "WorkingDir",
        "ExposedPorts",
        "Volumes",
        "StopSignal",
        "Healthcheck",
        "Shell",
    )
    ignored_labels = set()

    def first_mapping(value):
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value[0]
        return value if isinstance(value, dict) else {}

    def image_config(image):
        if not isinstance(image, dict):
            return {}
        value = image.get("config")
        if isinstance(value, dict):
            return value
        value = image.get("Config")
        return value if isinstance(value, dict) else {}

    def platform_view(image):
        image = first_mapping(image)
        os_value = image.get("os", image.get("Os", ""))
        arch_value = image.get("architecture", image.get("Architecture", ""))
        variant = image.get("variant", image.get("Variant", "")) or ""
        return {"os": os_value or "", "architecture": arch_value or "", "variant": variant}

    def normalized_config(image):
        cfg = image_config(first_mapping(image))
        out = {field: cfg.get(field) for field in config_fields}
        labels = cfg.get("Labels")
        if labels is None:
            labels = cfg.get("labels")
        if not isinstance(labels, dict):
            labels = {}
        out["Labels"] = {
            str(k): labels[k]
            for k in sorted(labels)
            if str(k) not in ignored_labels
        }
        return out

    def image_version_label(image):
        cfg = image_config(first_mapping(image))
        labels = cfg.get("Labels")
        if labels is None:
            labels = cfg.get("labels")
        if not isinstance(labels, dict):
            return ""
        for key in ("org.opencontainers.image.version", "version"):
            value = labels.get(key)
            if isinstance(value, (str, int, float)) and str(value).strip():
                return str(value).strip()
        return ""

    def recursive_oci_version(value):
        if isinstance(value, dict):
            candidate_value = value.get("org.opencontainers.image.version")
            if isinstance(candidate_value, (str, int, float)) and str(candidate_value).strip():
                return str(candidate_value).strip()
            for child in value.values():
                found = recursive_oci_version(child)
                if found:
                    return found
        elif isinstance(value, list):
            for child in value:
                found = recursive_oci_version(child)
                if found:
                    return found
        return ""

    candidate_image = first_mapping(candidate.get("source", {}).get("image_inspect", {}))
    candidate_view = {
        "platform": platform_view(candidate_image),
        "actual_version": str(candidate.get("actual_version", "")).strip(),
        "config": normalized_config(candidate_image),
    }

    registries = {}
    any_changed = False
    any_unknown = False
    has_observable_baseline = False

    for registry_name in ("dockerhub", "ghcr"):
        registry = baseline.get("registries", {}).get(registry_name, {})
        registry_status = registry.get("status", "inspect_failed")
        result = "UNKNOWN"
        promotion_required = False
        published_view = None
        reasons = []

        if registry_status == "missing":
            result = "MISSING"
            promotion_required = True
        elif registry_status == "unobservable":
            result = "UNOBSERVABLE"
            reasons.append("anonymous_inspect_not_authorized")
        elif registry_status != "present":
            result = "UNKNOWN"
            any_unknown = True
            reasons.append(f"registry_status={registry_status}")
        else:
            platform_data = registry.get("source", {}).get("platforms", {}).get(platform, {})
            if platform_data.get("status") != "present" or not isinstance(platform_data.get("image"), dict):
                result = "MISSING"
                promotion_required = True
            else:
                published_image = platform_data["image"]
                remote_version = image_version_label(published_image)
                if not remote_version:
                    remote_version = recursive_oci_version(registry.get("source", {}).get("parsed", {}))
                published_view = {
                    "platform": platform_view(published_image),
                    "actual_version": remote_version,
                    "config": normalized_config(published_image),
                }
                if not remote_version:
                    result = "UNKNOWN"
                    any_unknown = True
                    reasons.append("published_actual_version_missing")
                elif published_view == candidate_view:
                    has_observable_baseline = True
                    result = "SAME"
                else:
                    has_observable_baseline = True
                    result = "CHANGED"
                    promotion_required = True
                    any_changed = True
                    if published_view["platform"] != candidate_view["platform"]:
                        reasons.append("platform")
                    if published_view["actual_version"] != candidate_view["actual_version"]:
                        reasons.append("actual_version")
                    if published_view["config"] != candidate_view["config"]:
                        reasons.append("runtime_config_or_labels")

        registries[registry_name] = {
            "inspect_status": registry_status,
            "result": result,
            "promotion_required": promotion_required,
            "published_view": published_view,
            "reasons": reasons,
        }

    all_missing = all(registry["result"] == "MISSING" for registry in registries.values())
    explicit_missing_repair = (
        mode == "build"
        and any(registry["result"] == "MISSING" for registry in registries.values())
        and all(
            registry["result"] in {"MISSING", "UNOBSERVABLE"}
            for registry in registries.values()
        )
    )
    if not has_observable_baseline and not all_missing and not explicit_missing_repair:
        any_unknown = True
    if any_changed:
        for registry in registries.values():
            registry["promotion_required"] = True

    overall = (
        "UNKNOWN"
        if any_unknown
        else "CHANGED"
        if any_changed
        else "REPAIR"
        if explicit_missing_repair
        else "SAME"
    )
    result = {
        "schema_version": 1,
        "platform": platform,
        "candidate_view": candidate_view,
        "comparison": {
            "result": overall,
            "candidate_changed": any_changed,
        },
        "registries": registries,
    }
    Path(out_path).write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
