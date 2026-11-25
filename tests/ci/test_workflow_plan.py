#!/usr/bin/env python3
# Requirements: daily, manual and AdGuard release runs share the sole Container builder.
# Unknowns/research: live runner capacity and deferred applications require separate CI evidence.
# Optimization: pure selection and CLI fixtures do not need Docker or network.
# Risks/verification: share daily selection across schedule and dispatch and keep destination tags distinct.
"""Exercise the one-input Container plan and event isolation."""
import copy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import catalog
import workflow_plan

ROOT = Path(__file__).resolve().parents[2]


def reencode_probe(source, app):
    probe = catalog.embedded_meta_from_text(source)[app]
    encoded = catalog.encode_embedded_test(probe)
    return source.replace(encoded, catalog.encode_embedded_test(probe + '# fixture\n'), 1)


class WorkflowPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = catalog.catalog_from_readme(ROOT / 'README.md')

    def make(self, event='workflow_dispatch', **inputs):
        return workflow_plan.plan(self.config, event, inputs)

    def test_default_and_blank_select_vlmcsd_all_platforms(self):
        expected = self.make()
        self.assertEqual(expected['build'], 'true')
        self.assertEqual(expected['monitor'], 'false')
        self.assertEqual(expected['version_matrix'], {'include': []})
        rows = expected['build_targets']['include']
        self.assertEqual([(t['app_branch'],t['build_tag']) for t in rows], [('vlmcsd','latest')])
        self.assertEqual(rows[0]['arch_branch'], 'linux/amd64,linux/arm64,linux/386')
        for value in ['', ' ', '\t']:
            self.assertEqual(self.make(targets=value), expected)

    def test_bare_application_requires_unique_configured_tag(self):
        for app in ['runner', 'samba', 'adguardvpn-cli']:
            with self.subTest(app=app), self.assertRaisesRegex(ValueError, 'Tag required'):
                self.make(targets=app)
        row = self.make(targets='baidunetdisk')['build_targets']['include'][0]
        self.assertEqual((row['tag_repo'], row['dockerfile']), ('dev', 'dev.Dockerfile'))

    def test_explicit_target_preserves_catalog_configuration(self):
        row = self.make(targets='samba:alpine')['build_targets']['include'][0]
        for key, value in catalog.get(self.config, 'samba', 'alpine').items():
            self.assertEqual(row[key], value)
        self.assertNotIn('custom_env', row)
        self.assertNotIn('runner_image', row)
        self.assertNotIn('target_id', row)

    def test_unknown_malformed_and_nonstring_targets_fail(self):
        for value in [None, False, 5, [], {}, 'missing', '../vlmcsd', 'vlmcsd:missing', 'vlmcsd:',
                      'vlmcsd:latest:extra', ':latest', ',vlmcsd', 'vlmcsd,', 'vlmcsd,,aria2',
                      'all,vlmcsd', 'vlmcsd\n', 'vlmcsd\r', 'vlmcsd\0', '$(id)', 'vlmcsd;id']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.make(targets=value)

    def test_duplicate_aliases_are_rejected(self):
        for value in ['vlmcsd,vlmcsd', 'vlmcsd,vlmcsd:latest', 'samba:alpine,samba:alpine']:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Duplicate target'):
                self.make(targets=value)

    def test_list_preserves_selected_targets_order_without_substitution(self):
        rows = self.make(targets=' samba:alpine , aria2 ')['build_targets']['include']
        self.assertEqual([(r['app_branch'], r['build_tag']) for r in rows],
                         [('samba', 'alpine'), ('aria2', 'latest')])
        self.assertEqual([r['arch_branch'] for r in rows], ['linux/amd64,linux/arm64'] * 2)

    def test_all_covers_30_targets_and_52_platform_combinations_exactly_once(self):
        rows = self.make(targets='all')['build_targets']['include']
        actual = [(r['app_branch'], r['build_tag'], p) for r in rows for p in r['arch_branch'].split(',')]
        expected = {(app, catalog.target_tag(t), p) for app, meta in self.config['apps'].items()
                    for t in meta['targets'] for p in meta['platforms']}
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(actual), len(set(actual)))
        self.assertEqual((len(rows), len(actual), len({r['app_branch'] for r in rows})), (30, 52, 24))

    def test_representative_subset_needs_no_second_builder(self):
        rows = self.make(targets='aria2,samba:alpine,vlmcsd,runner:actions-slim')['build_targets']['include']
        self.assertEqual(len(rows), 4)
        self.assertEqual(sum(len(r['arch_branch'].split(',')) for r in rows), 8)

    def test_missing_default_is_not_replaced_but_all_has_no_hidden_dependency(self):
        config = copy.deepcopy(self.config)
        del config['apps']['vlmcsd']
        with self.assertRaises(ValueError):
            workflow_plan.plan(config, 'workflow_dispatch', {})
        self.assertEqual(len(workflow_plan.plan(config, 'workflow_dispatch', {'targets':'all'})['build_targets']['include']), 29)

    def test_duplicate_catalog_targets_fail_before_outputs(self):
        config = copy.deepcopy(self.config)
        config['apps']['vlmcsd']['targets'].append({'tag':'latest'})
        with self.assertRaises(ValueError):
            workflow_plan.plan(config, 'workflow_dispatch', {})

    def test_push_only_validates_and_does_not_parse_commit_messages(self):
        result = self.make('push', targets='all')
        self.assertEqual((result['build'], result['monitor']), ('false', 'false'))
        self.assertEqual(result['build_targets'], {'include': []})
        self.assertEqual(result['version_matrix'], {'include': []})

    def test_release_push_and_explicit_dispatch_select_the_same_release_target(self):
        result = workflow_plan.plan(self.config, 'push', {}, push_targets='adguardvpn-cli:release')
        self.assertEqual(result['build'], 'true')
        self.assertEqual(result['monitor'], 'false')
        release = catalog.get(self.config, 'adguardvpn-cli', 'release')
        self.assertEqual(result['build_targets'], {'include': [release]})
        manual = self.make(targets='adguardvpn-cli:release')
        self.assertEqual(manual['build_targets'], result['build_targets'])

    def test_push_diff_selects_daily_for_shared_pipeline_and_detects_release_inputs(self):
        readme = ROOT / 'README.md'
        source = readme.read_text(encoding='utf-8')
        changed_probe = reencode_probe(source, 'adguardvpn-cli')
        other_app = reencode_probe(source, 'aria2')
        before = '1' * 40
        fixtures = [('README.md\n', other_app, None),
                    ('README.md\n', changed_probe, 'adguardvpn-cli:release'),
                    ('application/adguardvpn-cli/release.Dockerfile\n', '', 'adguardvpn-cli:release'),
                    ('scripts/ci/publish-accepted-image.sh\n', '', 'daily'),
                    ('', '', None)]
        for paths, previous, expected in fixtures:
            with self.subTest(paths=paths, expected=expected), mock.patch(
                    'workflow_plan.subprocess.check_output', side_effect=[paths, previous]) as command:
                self.assertEqual(workflow_plan.changed_push_targets(before, readme), expected)
                self.assertIn(before, command.call_args_list[0].args[0])
                self.assertNotIn('application/adguardvpn-cli/nightly.Dockerfile', command.call_args_list[0].args[0])

    def test_schedule_builds_daily_and_monitors_all_apps_with_existing_tag_policy(self):
        result = self.make('schedule', targets='aria2')
        self.assertEqual((result['build'], result['monitor']), ('true', 'true'))
        versions = result['version_matrix']['include']
        self.assertEqual({r['app_branch'] for r in versions}, set(self.config['apps']))
        self.assertTrue(all(r['tag_repo'] == 'latest' for r in versions))
        manual = self.make(targets='daily')
        self.assertEqual((manual['build'], manual['monitor']), ('true', 'false'))
        self.assertEqual(result['build_targets'], manual['build_targets'])
        push = workflow_plan.plan(self.config, 'push', {}, push_targets='daily')
        self.assertEqual(push['monitor'], 'false')
        self.assertEqual(push['build_targets'], result['build_targets'])
        rows = result['build_targets']['include']
        self.assertGreater(len({row['app_branch'] for row in rows}) * 2, len(self.config['apps']))
        self.assertGreater(len(rows) * 2, len(self.make(targets='all')['build_targets']['include']))
        for row in rows:
            self.assertEqual(row, catalog.get(self.config, row['app_branch'], row['build_tag']))

    def test_novnc_targets_use_distinct_publication_tags(self):
        rows = self.make(targets='novnc,novnc_alpine')['build_targets']['include']
        self.assertEqual([(row['build_tag'], row['publish_tag']) for row in rows],
                         [('latest', 'latest'), ('latest', 'alpine')])
        config = copy.deepcopy(self.config)
        config['apps']['novnc_alpine']['targets'][0].pop('publish_tag')
        with self.assertRaisesRegex(ValueError, 'share a Docker Hub destination'):
            workflow_plan.plan(config, 'schedule', {})

    def test_removed_controls_and_non_objects_fail(self):
        for key in ['verify','execution_route','app_branch','tag_repo','target_id','build_matrix','platform',
                    'force_build','diagnostic_mode','layer_profile','image_name','dev_mode','custom_env','publish']:
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Only targets input'):
                self.make(**{key:'true'})
        for value in [None, [], 'targets=vlmcsd', False, 1]:
            with self.assertRaises(ValueError):
                workflow_plan.plan(self.config, 'workflow_dispatch', value)

    def test_external_events_remain_unsupported(self):
        for event in ['pull_request','workflow_call','repository_dispatch','unknown']:
            with self.assertRaises(ValueError):
                self.make(event)

    def test_diagnostics_are_fixed_and_shared(self):
        result = self.make(targets='all')
        self.assertEqual(set(result['images']), {'debian:latest','ubuntu:latest','alpine:latest','debian:sid','ubuntu:devel'})
        self.assertEqual(len(result['image_platforms']), 10)
        self.assertEqual({(r['image_name'],r['arch']) for r in result['image_platforms']},
                         {(image,arch) for image in result['images'] for arch in ['amd64','arm64']})

    def test_catalog_changes_flow_into_container_without_mutation(self):
        config, inputs = copy.deepcopy(self.config), {'targets':'samba:alpine'}
        target = next(t for t in config['apps']['samba']['targets'] if t['tag']=='alpine')
        target['base_image'], target['build_arg'] = 'example:changed','example-argument'
        before = copy.deepcopy((config,inputs))
        row = workflow_plan.plan(config,'workflow_dispatch',inputs)['build_targets']['include'][0]
        self.assertEqual((row['base_image'],row['build_arg']),('example:changed','example-argument'))
        self.assertEqual((config,inputs),before)

    def test_actual_cli_outputs_no_retired_switches_or_commit_message_route(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)/'output'
            env = dict(GITHUB_EVENT_NAME='workflow_dispatch',WORKFLOW_INPUTS='{"targets":"all"}',GITHUB_OUTPUT=str(output))
            with mock.patch.dict(os.environ,env), mock.patch('builtins.print'):
                workflow_plan.main()
            values = dict(line.split('=',1) for line in output.read_text().splitlines())
            self.assertEqual(len(json.loads(values['build_targets'])['include']),30)
            self.assertEqual(set(values), {'build', 'monitor',
                                           'version_matrix', 'build_targets', 'images', 'image_platforms'})
            output.unlink()
            with mock.patch.dict(os.environ,dict(env,WORKFLOW_INPUTS='{"verify":true}')), self.assertRaises(ValueError):
                workflow_plan.main()
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
