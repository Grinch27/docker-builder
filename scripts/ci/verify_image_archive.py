#!/usr/bin/env python3
# Requirements: verify Docker-save platform and the complete compressed export set.
# Unknowns/research: OCI layout exports are outside this Docker-save artifact contract.
# Risks/verification: reject missing/extra outputs, corrupt xz, split gaps and checksum mismatches.
# Optimization: stream decompression and hashes without reconstructing large archives on disk.
"""Verify the platform recorded inside a Docker-save tar archive."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tarfile
import tempfile


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


def checksum(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_outputs(root: Path, manifest_path: Path, platforms: str) -> dict:
    """Check output completeness and byte parity with already platform-verified tar files."""
    expected = platforms.split(",")
    records = json.loads(manifest_path.read_text(encoding="utf-8"))["archives"]
    if (not expected or len(set(expected)) != len(expected) or len(records) != len(expected)
            or {row["platform"] for row in records} != set(expected)):
        raise ValueError("Export manifest does not cover each configured platform exactly once")
    files, archives, seen = [], [], set()
    for row in records:
        name = row["filename"]
        if (not isinstance(name, str) or Path(name).name != name or not name.endswith(".tar")
                or not re.fullmatch(r"[A-Za-z0-9_.-]+", name)
                or not re.fullmatch(r"[a-f0-9]{64}", row["sha256"])):
            raise ValueError("Invalid archive name or checksum")
        whole = root / (name + ".xz")
        parts = sorted((root / "file-split").glob(name + ".xz.part*"))
        if whole.exists() and parts:
            raise ValueError("Ambiguous whole and split archive: " + name)
        paths = [whole] if whole.exists() else parts
        if not paths:
            raise ValueError("Missing compressed archive: " + name)
        if parts and [p.name for p in parts] != [name + f".xz.part{i:03d}" for i in range(1, len(parts) + 1)]:
            raise ValueError("Missing or invalid split sequence: " + name)
        for path in paths:
            if path.is_symlink() or path.parent.is_symlink() or not path.is_file() or not path.stat().st_size:
                raise ValueError("Output must be a nonempty regular file: " + str(path))
            relative = path.relative_to(root).as_posix()
            if relative in seen:
                raise ValueError("Duplicate archive filename: " + relative)
            seen.add(relative)
            files.append(dict(filename=relative, checksum=checksum(path)))
        # Separate processes avoid buffering entire tar/xz streams in memory or on disk.
        with tempfile.TemporaryFile() as errors:
            with subprocess.Popen(["cat", "--", *map(str, paths)], stdout=subprocess.PIPE, stderr=errors) as source:
                with subprocess.Popen(["xz", "--decompress", "--stdout"], stdin=source.stdout,
                                      stdout=subprocess.PIPE, stderr=errors) as decoder:
                    source.stdout.close()
                    actual = hashlib.file_digest(decoder.stdout, "sha256").hexdigest()
                    decoder.stdout.close()
                    decoded = decoder.wait()
                copied = source.wait()
            if copied or decoded:
                errors.seek(0)
                raise ValueError("Invalid compressed archive: " + errors.read(4096).decode(errors="replace"))
        if actual != row["sha256"]:
            raise ValueError("Decompressed archive checksum mismatch: " + name)
        archives.append(dict(row, files=[p.relative_to(root).as_posix() for p in paths]))
    actual_files = {p.relative_to(root).as_posix() for p in root.rglob("*")
                    if p.is_file() or p.is_symlink()}
    if actual_files != seen:
        raise ValueError("Unexpected or missing output files: " + str(sorted(actual_files ^ seen)))
    return dict(files=files, archives=archives)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, nargs="?")
    parser.add_argument("platform", nargs="?")
    parser.add_argument("--outputs", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--platforms")
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    if args.outputs:
        if not all([args.manifest, args.platforms, args.metadata]) or args.archive or args.platform:
            parser.error("--outputs requires --manifest, --platforms and --metadata only")
        result = verify_outputs(args.outputs, args.manifest, args.platforms)
        args.metadata.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(f"Compressed exports PASS: {len(result['archives'])} platforms, {len(result['files'])} files")
        return
    if not args.archive or not args.platform or any([args.manifest, args.platforms, args.metadata]):
        parser.error("supply archive and platform, or the complete --outputs contract")
    result = verify(args.archive, args.platform)
    print(f"Archive platform PASS: expected={args.platform} actual={result['platform']} layers={result['layers']}")


if __name__ == "__main__":
    main()
