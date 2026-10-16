#!/usr/bin/env python3
"""Offline regression tests for the README catalog. No Docker or network access."""
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import catalog  # noqa: E402


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = catalog.catalog_from_readme(ROOT / "README.md")

    def test_catalog_covers_exactly_all_app_directories(self):
        stats = catalog.validate(self.config, ROOT)
        self.assertEqual(stats["apps"], 24)
        self.assertEqual(stats["targets"], 30)
        dirs = {x.name for x in (ROOT / "application").iterdir()
                if x.is_dir() and not x.name.startswith(".")}
        self.assertEqual(dirs, set(self.config["apps"]))
        self.assertEqual(stats["legacy_ref_conflicts"],
                         {"grinch27/novnc:latest": ["novnc", "novnc_alpine"]})

    def test_all_target_settings_are_resolvable(self):
        for name, app in self.config["apps"].items():
            for target in app["targets"]:
                with self.subTest(app=name, tag=target["tag"]):
                    item = catalog.get(self.config, name, target["tag"])
                    self.assertTrue((ROOT / "application" / name / "build" /
                                     item["dockerfile"]).is_file())
                    self.assertTrue(item["repo_dockerhub"].startswith("grinch27/"))
                    self.assertNotIn("\n", item["base_image"])
                    self.assertEqual(item["tag_repo"], target["tag"])
                    self.assertEqual(item["arch_branch"],
                                     ",".join(app["platforms"]))

    def test_matrices_have_distinct_work_and_no_implicit_targets(self):
        vs = catalog.matrix(self.config, "version", "ubuntu-test")["include"]
        bs = catalog.matrix(self.config, "build", "ubuntu-test")["include"]
        self.assertEqual(len(vs), 24)
        self.assertEqual(len(bs), 30)
        self.assertEqual({i["app_branch"] for i in vs}, set(self.config["apps"]))
        self.assertEqual(len({(i["app_branch"], i["tag_repo"]) for i in bs}), 30)
        self.assertTrue(all(i["runner_image"] == "ubuntu-test" for i in vs + bs))

    def test_target_overrides(self):
        alpine = catalog.get(self.config, "samba", "alpine")
        self.assertEqual(alpine["base_image"], "alpine:latest")
        self.assertEqual(alpine["dockerfile"], "alpine.Dockerfile")
        self.assertEqual(catalog.get(self.config, "runner", "actions")["dockerfile"],
                         "actions.Dockerfile")
        self.assertEqual(catalog.get(self.config, "runner", "actions-slim")["dockerfile"],
                         "actions-slim.Dockerfile")
        self.assertEqual(catalog.get(self.config, "sdnext-dev", "dev")["build_arg"],
                         "therock_version=7.11.0,therock_release_type=stable,therock_amdgpu_family=gfx110X-all")

    def test_four_tag_policies(self):
        cases = [
            ("runner", "actions", "1.2.3", ["actions"]),
            ("curl", "latest", "1.2.3", ["latest", "latest-1.2.3"]),
            ("dnscrypt-proxy", "latest", "1.2.3", ["latest", "1.2.3"]),
            ("sdnext", "latest", "1.2.3 RC1", ["latest", "1.2.3-RC1"]),
            ("adguardvpn-cli", "nightly", "1.2.3", ["nightly", "nightly-1.2.3"]),
        ]
        for app, tag, version, expected in cases:
            with self.subTest(app=app, tag=tag):
                item = catalog.get(self.config, app, tag)
                self.assertEqual(catalog.tags(item, version, True), expected)
                self.assertEqual(catalog.tags(item, version, False), [tag])

    def test_reject_unregistered_application_directories(self):
        changed = copy.deepcopy(self.config)
        del changed["apps"]["aria2"]
        with self.assertRaisesRegex(ValueError, "Unregistered application"):
            catalog.validate(changed, ROOT)

    def test_reject_invalid_or_missing_target(self):
        changed = copy.deepcopy(self.config)
        changed["apps"]["runner"]["targets"].append(
            copy.deepcopy(changed["apps"]["runner"]["targets"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            catalog.validate(changed, ROOT)
        with self.assertRaisesRegex(ValueError, "Unknown target"):
            catalog.get(self.config, "runner", "not-a-target")

    def test_write_is_idempotent_and_preserves_generated_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "application").symlink_to(ROOT / "application", target_is_directory=True)
            path = directory / "README.md"
            shutil.copyfile(ROOT / "README.md", path)
            old = path.read_text(encoding="utf-8")
            marker = "<!-- app-version-table:start -->"
            self.assertIn(marker, old)
            self.assertEqual(catalog.update(path, copy.deepcopy(self.config),
                                            "runner", "base_image", "debian:stable-slim"),
                             "updated")
            first = path.read_text(encoding="utf-8")
            refreshed = catalog.catalog_from_readme(path)
            self.assertEqual(catalog.update(path, refreshed, "runner",
                                            "base_image", "debian:stable-slim"), "unchanged")
            self.assertEqual(first, path.read_text(encoding="utf-8"))
            self.assertEqual(old.split(marker, 1)[1], first.split(marker, 1)[1])
            self.assertEqual(catalog.catalog_from_readme(path), refreshed)

    def test_reject_broken_readme_markers(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "application").symlink_to(ROOT / "application", target_is_directory=True)
            path = directory / "README.md"
            path.write_text((ROOT / "README.md").read_text().replace(
                catalog.END, "", 1), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "marker pair"):
                catalog.catalog_from_readme(path)

    def test_target_setting_update_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "application").symlink_to(ROOT / "application", target_is_directory=True)
            readme = directory / "README.md"
            shutil.copyfile(ROOT / "README.md", readme)
            original = readme.read_text(encoding="utf-8")
            self.assertEqual(catalog.update(readme, copy.deepcopy(self.config),
                                            "samba", "base_image", "alpine:edge",
                                            scope="target", tag="alpine"), "updated")
            result = catalog.catalog_from_readme(readme)
            self.assertEqual(catalog.get(result, "samba", "alpine")["base_image"],
                             "alpine:edge")
            self.assertEqual(catalog.get(result, "samba", "latest")["base_image"],
                             "debian:testing-slim")
            self.assertEqual(catalog.update(readme, result, "samba", "base_image",
                                            "alpine:edge", scope="target",
                                            tag="alpine"), "unchanged")
            self.assertEqual(original.split(catalog.END, 1)[1],
                             readme.read_text(encoding="utf-8").split(catalog.END, 1)[1])

    def test_reject_unsafe_target_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "application").symlink_to(ROOT / "application", target_is_directory=True)
            readme = directory / "README.md"
            shutil.copyfile(ROOT / "README.md", readme)
            with self.assertRaisesRegex(ValueError, "missing Dockerfile"):
                catalog.update(readme, copy.deepcopy(self.config), "runner",
                               "dockerfile", "missing.Dockerfile",
                               scope="target", tag="actions")
            with self.assertRaisesRegex(ValueError, "Unknown target"):
                catalog.update(readme, copy.deepcopy(self.config), "runner",
                               "dockerfile", "Dockerfile",
                               scope="target", tag="unknown")

    def test_reject_unknown_fields_in_every_scope(self):
        c = copy.deepcopy(self.config)
        c['build_targtes'] = []
        with self.assertRaisesRegex(ValueError, 'Unknown catalog fields'):
            catalog.validate(c, ROOT)

        c = copy.deepcopy(self.config)
        c['apps']['runner']['platfroms'] = ['linux/amd64']
        with self.assertRaisesRegex(ValueError, 'unknown app fields'):
            catalog.validate(c, ROOT)

        c = copy.deepcopy(self.config)
        c['apps']['runner']['targets'][0]['base_iamge'] = 'alpine:latest'
        with self.assertRaisesRegex(ValueError, 'unknown target fields'):
            catalog.validate(c, ROOT)

    def test_reject_nonobject_application(self):
        c = copy.deepcopy(self.config)
        c['apps']['runner'] = []
        with self.assertRaisesRegex(ValueError, 'app must be object'):
            catalog.validate(c, ROOT)


if __name__ == "__main__":
    unittest.main(verbosity=2)
