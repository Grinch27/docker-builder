#!/usr/bin/env python3
# Requirements: verify per-platform archive identity, not filenames or checksum differences.
# Unknowns/research: Docker CLI integration is verified by the gpt_dev.yml real build Job.
# Risks/verification: mixed platforms, wrong variants, missing config/layers and invalid selectors.
# Optimization: small synthetic tar fixtures exercise the artifact contract without Docker.
"""Tests for inspecting Docker-save archive platform metadata."""

import io
import hashlib
import lzma
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

    def compressed(self, directory, split=False):
        root = Path(directory)
        output = root / "output"
        output.mkdir()
        tar = self.archive(directory, ["amd64"])
        raw = tar.read_bytes()
        data = lzma.compress(raw, check=lzma.CHECK_SHA256)
        manifest = root / "exports.json"
        manifest.write_text(json.dumps({"archives":[dict(platform="linux/amd64",filename="image.tar",sha256=hashlib.sha256(raw).hexdigest())]}))
        if split:
            parts = output / "file-split"
            parts.mkdir()
            for i, start in enumerate(range(0,len(data),31),1):
                (parts / f"image.tar.xz.part{i:03d}").write_bytes(data[start:start+31])
        else:
            (output / "image.tar.xz").write_bytes(data)
        return output, manifest

    def test_whole_and_split_xz_match_original_tar_checksum(self):
        for split in [False,True]:
            with self.subTest(split=split), tempfile.TemporaryDirectory() as directory:
                output, manifest = self.compressed(directory,split)
                result = verify_image_archive.verify_outputs(output,manifest,"linux/amd64")
                self.assertEqual(len(result["archives"]),1)
                self.assertTrue(result["files"])
                self.assertTrue(all(len(r['checksum'])==64 for r in result['files']))

    def test_empty_outputs_and_invalid_manifest_platform_sets_fail(self):
        for mutate, platforms in [(lambda o,m:(o/"image.tar.xz").unlink(),"linux/amd64"),
                                  (lambda o,m:None,"linux/amd64,linux/arm64"),
                                  (lambda o,m:None,"linux/amd64,linux/amd64"),
                                  (lambda o,m:m.write_text('{"archives":[]}'),"linux/amd64")]:
            with tempfile.TemporaryDirectory() as directory:
                output,manifest=self.compressed(directory)
                mutate(output,manifest)
                with self.assertRaises(ValueError):
                    verify_image_archive.verify_outputs(output,manifest,platforms)

    def test_corrupt_truncated_and_wrong_content_xz_fail(self):
        for data in [b"not-xz",lzma.compress(b"wrong tar bytes"),lzma.compress(b"data")[:-8]]:
            with tempfile.TemporaryDirectory() as directory:
                output,manifest=self.compressed(directory)
                (output/"image.tar.xz").write_bytes(data)
                with self.assertRaises(ValueError):
                    verify_image_archive.verify_outputs(output,manifest,"linux/amd64")

    def test_split_gaps_missing_last_and_bad_first_index_fail(self):
        for index in [0,1,-1]:
            with tempfile.TemporaryDirectory() as directory:
                output,manifest=self.compressed(directory,True)
                parts=sorted((output/'file-split').iterdir())
                parts[index].unlink()
                with self.assertRaises(ValueError):
                    verify_image_archive.verify_outputs(output,manifest,"linux/amd64")

    def test_extra_files_ambiguous_whole_and_split_and_symlink_fail(self):
        for kind in ['extra','both','symlink']:
            with tempfile.TemporaryDirectory() as directory:
                output,manifest=self.compressed(directory)
                if kind=='extra':
                    (output/'extra.tar.xz').write_bytes(b'fixture')
                elif kind=='both':
                    (output/'file-split').mkdir()
                    (output/'file-split/image.tar.xz.part001').write_bytes(b'fixture')
                else:
                    compressed=output/'image.tar.xz'
                    compressed.rename(Path(directory)/'external.xz')
                    compressed.symlink_to(Path(directory)/'external.xz')
                with self.assertRaises(ValueError):
                    verify_image_archive.verify_outputs(output,manifest,"linux/amd64")

    def test_export_manifest_rejects_paths_duplicates_and_invalid_digests(self):
        for change in [{'filename':'../image.tar'},{'filename':'image.tar/x'},{'sha256':'invalid'}]:
            with tempfile.TemporaryDirectory() as directory:
                output,manifest=self.compressed(directory)
                data=json.loads(manifest.read_text())
                data['archives'][0].update(change)
                manifest.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    verify_image_archive.verify_outputs(output,manifest,"linux/amd64")


if __name__ == "__main__":
    unittest.main()
