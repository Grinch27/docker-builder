#!/usr/bin/env python3
# Requirements: verify per-platform archive identity, not filenames or checksum differences.
# Unknowns/research: Docker CLI integration is verified by the gpt_dev.yml real build Job.
# Risks/verification: mixed platforms, wrong variants, missing config/layers and invalid selectors.
# Optimization: small synthetic tar fixtures exercise the artifact contract without Docker.
"""Tests for inspecting Docker-save archive platform metadata."""

import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import verify_image_archive


class ImageArchiveTests(unittest.TestCase):
    def archive(self, directory, architectures, variant=None, missing=None, os_name="linux"):
        path = Path(directory) / "image.tar"
        manifest, entries = [], {}
        for i, arch in enumerate(architectures):
            name = f"config-{i}.json"
            config = dict(os=os_name, architecture=arch)
            if variant:
                config["variant"] = variant
            entries[name] = json.dumps(config).encode()
            entries[f"layer-{i}.tar"] = b""
            manifest.append(dict(Config=name, Layers=[f"layer-{i}.tar"], RepoTags=["example:test"]))
        entries["manifest.json"] = json.dumps(manifest).encode()
        with tarfile.open(path, "w") as archive:
            for name, data in entries.items():
                if name == missing:
                    continue
                info = tarfile.TarInfo(name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        return path

    def test_configured_architectures(self):
        with tempfile.TemporaryDirectory() as directory:
            for arch in ["amd64", "arm64", "386"]:
                with self.subTest(architecture=arch):
                    path = self.archive(directory, [arch])
                    self.assertEqual(verify_image_archive.verify(path, "linux/" + arch)["platform"], "linux/" + arch)

    def test_wrong_platform_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.archive(directory, ["amd64"])
            with self.assertRaisesRegex(ValueError, "mismatch"):
                verify_image_archive.verify(path, "linux/arm64")

    def test_multi_platform_archive_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.archive(directory, ["amd64", "arm64", "386"])
            with self.assertRaisesRegex(ValueError, "exactly one"):
                verify_image_archive.verify(path, "linux/amd64")

    def test_variants_are_verified_when_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.archive(directory, ["arm"], variant="v7")
            self.assertEqual(verify_image_archive.verify(path, "linux/arm/v7")["platform"], "linux/arm/v7")
            with self.assertRaisesRegex(ValueError, "variant"):
                verify_image_archive.verify(path, "linux/arm/v6")

    def test_missing_required_archive_entries_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            for name in ["manifest.json", "config-0.json", "layer-0.tar"]:
                with self.subTest(missing=name):
                    path = self.archive(directory, ["amd64"], missing=name)
                    with self.assertRaises(KeyError):
                        verify_image_archive.verify(path, "linux/amd64")

    def test_wrong_os_and_invalid_platform_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.archive(directory, ["amd64"], os_name="windows")
            for platform in ["linux/amd64", "linux", "linux//amd64"]:
                with self.subTest(platform=platform), self.assertRaises(ValueError):
                    verify_image_archive.verify(path, platform)


if __name__ == "__main__":
    unittest.main()
