#!/usr/bin/env python3
# Requirements: each per-platform Docker archive must contain exactly that platform.
# Unknowns/research: OCI layout exports are outside this Docker-save artifact contract.
# Risks/verification: reject mixed/wrong platforms and incomplete manifests without extracting files.
# Optimization: inspect manifest/config JSON and layer entries; never unpack or execute image content.
"""Verify the platform recorded inside a Docker-save tar archive."""

import argparse
import json
from pathlib import Path
import tarfile


def verify(path: Path, platform: str) -> dict:
    expected = platform.split("/")
    if len(expected) not in {2, 3} or not all(expected):
        raise ValueError("Expected os/arch[/variant] platform")
    with tarfile.open(path, "r:*") as archive:
        def read_json(name):
            member = archive.getmember(name)
            if not member.isfile():
                raise ValueError("Archive JSON entry must be a regular file: " + name)
            with archive.extractfile(member) as stream:
                return json.load(stream)

        manifest = read_json("manifest.json")
        if not isinstance(manifest, list) or len(manifest) != 1:
            raise ValueError("Per-platform archive must have exactly one image manifest")
        entry = manifest[0]
        config = read_json(entry["Config"])
        actual = [config["os"], config["architecture"]]
        if actual != expected[:2]:
            raise ValueError(f"Archive platform mismatch: expected {platform}, found {'/'.join(actual)}")
        if len(expected) == 3 and config.get("variant") != expected[2]:
            raise ValueError("Archive variant mismatch: " + str(config.get("variant")))
        layers = entry.get("Layers")
        if not isinstance(layers, list) or not layers:
            raise ValueError("Archive image layers are missing")
        for layer in layers:
            if not archive.getmember(layer).isfile():
                raise ValueError("Archive layer must be a regular file: " + layer)
        return {"platform": "/".join(actual + ([config["variant"]] if config.get("variant") else [])),
                "layers": len(layers)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("platform")
    args = parser.parse_args()
    result = verify(args.archive, args.platform)
    print(f"Archive platform PASS: expected={args.platform} actual={result['platform']} layers={result['layers']}")


if __name__ == "__main__":
    main()
