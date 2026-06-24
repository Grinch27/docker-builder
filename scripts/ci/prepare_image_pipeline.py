#!/usr/bin/env python3
"""Prepare a stable matrix for the image pipeline workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TARGET_FIELDS = [
    "app_branch",
    "tag_repo",
    "custom_env",
    "runner_image",
    "force_push",
]


def dump_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def normalize_target(item: dict[str, Any]) -> dict[str, str]:
    target = {key: str(item.get(key, "")) for key in TARGET_FIELDS}
    if not target["app_branch"]:
        raise ValueError("matrix target is missing app_branch")
    target["tag_repo"] = target["tag_repo"] or "latest"
    target["runner_image"] = target["runner_image"] or "ubuntu-latest"
    target["force_push"] = target["force_push"] or "false"
    return target


def parse_matrix(raw: str) -> list[dict[str, str]]:
    raw = raw.strip()
    if not raw:
        return []
    data = json.loads(raw)
    if isinstance(data, dict):
        include = data.get("include", [])
    elif isinstance(data, list):
        include = data
    else:
        raise ValueError("build_matrix must be a JSON object with include or a JSON array")

    if not isinstance(include, list):
        raise ValueError("build_matrix include must be a JSON array")
    return [normalize_target(item) for item in include if isinstance(item, dict)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-matrix", default="")
    parser.add_argument("--app-branch", default="")
    parser.add_argument("--tag-repo", default="latest")
    parser.add_argument("--custom-env", default="")
    parser.add_argument("--runner-image", default="ubuntu-latest")
    parser.add_argument("--force-push", default="false")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    include = parse_matrix(args.build_matrix)
    if not include:
        include = [
            normalize_target(
                {
                    "app_branch": args.app_branch,
                    "tag_repo": args.tag_repo,
                    "custom_env": args.custom_env,
                    "runner_image": args.runner_image,
                    "force_push": args.force_push,
                }
            )
        ]

    matrix = {"include": include}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(dump_json(matrix), encoding="utf-8")
    print(dump_json(matrix), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
