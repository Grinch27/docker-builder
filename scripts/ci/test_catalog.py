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

    def test_24_canonical_test_scripts_in_readme_table(self):
        tests=catalog.embedded_tests_from_text((ROOT/'README.md').read_text(encoding='utf-8'))
        self.assertEqual(len(tests),24)
        self.assertEqual(set(tests),set(self.config['apps']))
        self.assertTrue(all(s.startswith('#!/bin/sh') for s in tests.values()))

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
            marker = "<!-- app-config:end -->"
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

    def test_summary_matches_canonical_json(self):
        self.assertTrue(catalog.check_summary(ROOT/'README.md',self.config))
        view=catalog.render_summary(self.config)
        self.assertEqual(view.count('](application/'),24)
        self.assertIn('alpine.Dockerfile',view)

    def test_set_refreshes_summary_and_preserves_version_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            (directory/'application').symlink_to(ROOT/'application',target_is_directory=True)
            path=directory/'README.md'
            shutil.copyfile(ROOT/'README.md',path)
            old=path.read_text(encoding='utf-8')
            self.assertEqual(catalog.update(path,copy.deepcopy(self.config),'samba','base_image',
                'alpine:edge',scope='target',tag='alpine'),'updated')
            after=path.read_text(encoding='utf-8')
            self.assertIn('`alpine: alpine:edge`',after)
            self.assertTrue(catalog.check_summary(path,catalog.catalog_from_readme(path)))
            self.assertEqual(old.split(catalog.END,1)[1],after.split(catalog.END,1)[1])
            self.assertEqual(catalog.write_summary(path,catalog.catalog_from_readme(path)),'unchanged')

    def test_summary_staleness_detected_and_repaired(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp)
            (directory/'application').symlink_to(ROOT/'application',target_is_directory=True)
            path=directory/'README.md'
            current=(ROOT/'README.md').read_text(encoding='utf-8')
            path.write_text(current.replace('24 applications / 30 build targets',
                '23 applications / 30 build targets',1),encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'stale'):
                catalog.check_summary(path,catalog.catalog_from_readme(path))
            self.assertEqual(catalog.write_summary(path,catalog.catalog_from_readme(path)),'updated')
            self.assertTrue(catalog.check_summary(path,catalog.catalog_from_readme(path)))

    def test_collapsible_markers_are_unchanged_for_actions(self):
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        for marker in [catalog.START,catalog.END,catalog.SUMMARY_START,catalog.SUMMARY_END,
]:
            self.assertEqual(readme.count(marker),1,marker)
        self.assertEqual(catalog.catalog_from_readme(ROOT/'README.md'),self.config)
    def test_single_visible_table_contains_app_and_probe_data(self):
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertEqual(text.count('| Application |'),1)
        self.assertNotIn('<!-- app-version-table:start -->',text)
        self.assertIn('Detected version',text)
        self.assertEqual(text.split(catalog.SUMMARY_START,1)[1].split(catalog.SUMMARY_END,1)[0].count('](application/'),24)

    def test_v2_combines_config_and_historical_monitor_records(self):
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        document=catalog.catalog_document_from_text(source)
        self.assertEqual(document['schema_version'],2)
        self.assertEqual(set(document),{'schema_version','config','monitor'})
        self.assertEqual(document['config'],self.config)
        self.assertEqual(len(document['monitor']['records']),24)
        self.assertNotIn('<!-- app-version-json:start -->',source)

    def test_v2_monitor_only_update_preserves_config_and_is_idempotent(self):
        import monitor_state
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        versions=monitor_state.parse_readme_versions(source)
        updated=[dict(x) for x in versions]
        updated[0]['version']='new-version-test'
        rendered=monitor_state.render_readme(source,updated,'.github/workflows/docker_allinone.yml')
        self.assertEqual(catalog.catalog_data_from_text(rendered),self.config)
        self.assertEqual(monitor_state.parse_readme_versions(rendered),updated)
        self.assertEqual(monitor_state.render_readme(rendered,updated,
            '.github/workflows/docker_allinone.yml'),rendered)

    def test_v2_invalid_monitor_is_rejected(self):
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        doc=catalog.catalog_document_from_text(source)
        bad=copy.deepcopy(doc)
        bad['monitor']['records'].append(dict(bad['monitor']['records'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate monitor record'):
            catalog.validate_document(bad)
        bad=copy.deepcopy(doc)
        bad['monitor']['records'][0].pop('version')
        with self.assertRaisesRegex(ValueError,'Incomplete monitor record'):
            catalog.validate_document(bad)

    def test_v1_compatibility_reader(self):
        import monitor_state
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        old=catalog.replace_catalog_document(source,self.config)
        records=catalog.snapshot_from_readme(source)
        fence=chr(96)*3
        legacy=(old+'\n<!-- app-version-json:start -->\n'+fence+'json\n'+
                json.dumps(records,indent=2)+'\n'+fence+'\n<!-- app-version-json:end -->\n')
        self.assertEqual(catalog.catalog_data_from_text(legacy),self.config)
        self.assertEqual(len(monitor_state.parse_readme_versions(legacy)),24)
    def test_monitor_round_trip_keeps_config_and_summary(self):
        import monitor_state
        original=(ROOT/'README.md').read_text(encoding='utf-8')
        records=monitor_state.parse_readme_versions(original)
        self.assertEqual(len(records),24)
        self.assertEqual(len(records[0]),len(monitor_state.README_FIELDS))
        regenerated=monitor_state.render_readme(original,records,
            '.github/workflows/monitor-images.yml')
        self.assertEqual(regenerated,original)
        self.assertEqual(monitor_state.semantic_changed_apps(records,records),[])
        self.assertEqual(catalog.catalog_from_readme(ROOT/'README.md'),self.config)

    def test_monitor_refresh_does_not_modify_canonical_config(self):
        import monitor_state
        original=(ROOT/'README.md').read_text(encoding='utf-8')
        versions=monitor_state.parse_readme_versions(original)
        changed=[dict(r) for r in versions]
        changed[0]['version']='test-version-value'
        updated=monitor_state.render_readme(original,changed,
            '.github/workflows/docker_allinone.yml')
        self.assertEqual(catalog.catalog_data_from_text(original),
                         catalog.catalog_data_from_text(updated))
        self.assertNotEqual(catalog.snapshot_from_readme(original),
                            catalog.snapshot_from_readme(updated))
        self.assertNotEqual(original.split(catalog.SUMMARY_START,1)[1].split(catalog.SUMMARY_END,1)[0],
                            updated.split(catalog.SUMMARY_START,1)[1].split(catalog.SUMMARY_END,1)[0])
        self.assertEqual(len(monitor_state.parse_readme_versions(updated)),24)


if __name__ == "__main__":
    unittest.main(verbosity=2)
