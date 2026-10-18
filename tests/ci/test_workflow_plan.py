#!/usr/bin/env python3
# Requirements: two inputs preserve catalog-only builds, combined acceptance and event isolation.
# Unknowns/research: live runner scheduling and fixed diagnostics need separate CI evidence.
# Optimization: pure planner and actual CLI fixtures need no Docker or network.
# Risks/verification: boolean coercion, ambiguous aliases, retired inputs, full matrices and publication gates.
"""Exercise public inputs and the fixed nonpublishing plan end to end."""

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


class WorkflowPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = catalog.catalog_from_readme(ROOT / 'README.md')

    def make(self, event_name='workflow_dispatch', event=None, **inputs):
        return workflow_plan.plan(self.config, event_name, event or {}, inputs, 'resolved-runner')

    def test_default_dispatch_builds_one_configured_vlmcsd_target(self):
        result = self.make()
        self.assertEqual([t['target_id'] for t in result['build_targets']['include']], ['vlmcsd'])
        self.assertEqual(result['build_targets']['include'][0]['arch_branch'], 'linux/amd64,linux/arm64,linux/386')
        self.assertEqual({k: result[k] for k in ['build', 'verify', 'monitor', 'force_build', 'fetch_versions']},
                         dict(build='true', verify='false', monitor='true', force_build='true', fetch_versions='true'))
        self.assertEqual(result['test_matrix'], {'include': []})
        self.assertEqual(result['dev_matrix'], {'include': []})

    def test_empty_target_input_uses_the_same_default(self):
        for value in ['', ' ', '\t']:
            with self.subTest(value=value):
                self.assertEqual(self.make(targets=value), self.make())

    def test_boolean_and_string_false_cannot_start_acceptance(self):
        for value in [False, 'false']:
            with self.subTest(value=value):
                self.assertEqual(self.make(verify=value), self.make())

    def test_boolean_and_string_true_start_combined_acceptance(self):
        for value in [True, 'true']:
            with self.subTest(value=value):
                result = self.make(verify=value)
                self.assertEqual(result['verify'], 'true')
                self.assertEqual(result['build'], 'false')
                self.assertEqual(result['monitor'], 'false')
                self.assertEqual(result['fetch_versions'], 'true')
                self.assertEqual(result['force_build'], 'true')
                self.assertEqual(len(result['test_matrix']['include']), 3)

    def test_invalid_verify_values_are_rejected(self):
        for value in [None, 0, 1, [], {}, '', 'yes', 'TRUE', ' false', 'false\n']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.make(verify=value)

    def test_bare_application_requires_a_unique_tag(self):
        for app in ['runner', 'samba', 'adguardvpn-cli']:
            with self.subTest(app=app), self.assertRaisesRegex(ValueError, 'Tag required'):
                self.make(targets=app)
        target = self.make(targets='baidunetdisk')['build_targets']['include'][0]
        self.assertEqual((target['app_branch'], target['tag_repo'], target['dockerfile']),
                         ('baidunetdisk', 'dev', 'dev.Dockerfile'))

    def test_explicit_tag_preserves_all_catalog_settings(self):
        result = self.make(targets='samba:alpine')
        actual = result['build_targets']['include'][0]
        for key, value in catalog.get(self.config, 'samba', 'alpine').items():
            self.assertEqual(actual[key], value)
        self.assertEqual(actual['runner_image'], 'resolved-runner')
        self.assertEqual(actual['custom_env'], '')

    def test_unknown_malformed_and_nonstring_targets_fail(self):
        for value in [None, False, 5, [], {}, 'missing', '../vlmcsd', 'vlmcsd:missing', 'vlmcsd:',
                      'vlmcsd:latest:extra', ':latest', ',vlmcsd', 'vlmcsd,', 'vlmcsd,,aria2',
                      'all,vlmcsd', 'vlmcsd\n', 'vlmcsd\r', 'vlmcsd\0', '$(id)', 'vlmcsd;id',
                      'samba-alpine', 'vlmcsd:../latest']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.make(targets=value, verify=True)

    def test_duplicate_aliases_cannot_run_the_same_target_twice(self):
        for value in ['vlmcsd,vlmcsd', 'vlmcsd,vlmcsd:latest', 'samba:alpine,samba:alpine']:
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Duplicate target'):
                self.make(targets=value, verify=True)

    def test_multi_target_selection_preserves_order_and_all_platforms(self):
        result = self.make(targets=' samba:alpine , aria2 ', verify=True)
        matrix = result['test_matrix']['include']
        self.assertEqual([(t['app'], t['tag']) for t in matrix],
                         [('samba', 'alpine'), ('samba', 'alpine'), ('aria2', 'latest'), ('aria2', 'latest')])
        self.assertEqual({t['platform'] for t in matrix}, {'linux/amd64', 'linux/arm64'})

    def test_multiple_targets_and_all_require_explicit_acceptance(self):
        for value in ['vlmcsd,aria2', 'all']:
            for verify in [False, 'false']:
                with self.subTest(value=value, verify=verify), self.assertRaises(ValueError):
                    self.make(targets=value, verify=verify)

    def test_all_covers_every_configured_combination_exactly_once(self):
        matrix = self.make(targets='all', verify=True)['test_matrix']['include']
        expected = {(app, catalog.target_tag(t), platform) for app, meta in self.config['apps'].items()
                    for t in meta['targets'] for platform in meta['platforms']}
        actual = {(row['app'], row['tag'], row['platform']) for row in matrix}
        self.assertEqual(actual, expected)
        self.assertEqual(len(matrix), len(actual))
        self.assertEqual(len(actual), 52)
        self.assertEqual(len({app for app, tag, platform in actual}), 24)
        self.assertEqual(len({(app, tag) for app, tag, platform in actual}), 30)

    def test_subset_is_not_mislabeled_as_full_coverage(self):
        matrix = self.make(targets='aria2', verify=True)['test_matrix']['include']
        self.assertEqual(len(matrix), 2)
        self.assertEqual({row['app'] for row in matrix}, {'aria2'})

    def test_single_target_drives_both_dev_and_container_acceptance(self):
        result = self.make(targets='samba:alpine', verify=True)
        for key in ['build_targets', 'dev_matrix']:
            self.assertEqual([t['target_id'] for t in result[key]['include']], ['samba-alpine'])
        self.assertEqual(result['version_matrix']['include'][0]['app_branch'], 'samba')

    def test_multi_target_acceptance_uses_fixed_vlmcsd_representative(self):
        for targets in ['all', 'aria2,samba:alpine']:
            with self.subTest(targets=targets):
                result = self.make(targets=targets, verify=True)
                for key in ['build_targets', 'dev_matrix']:
                    self.assertEqual([t['target_id'] for t in result[key]['include']], ['vlmcsd'])
                self.assertEqual(len(result['version_matrix']['include']), 1)
                self.assertEqual(result['version_matrix']['include'][0]['app_branch'], 'vlmcsd')

    def test_dev_destination_does_not_change_novnc_container_target(self):
        result = self.make(targets='novnc_alpine', verify=True)
        dev, container = [result[key]['include'][0] for key in ['dev_matrix', 'build_targets']]
        self.assertEqual((dev['tag_repo'], dev['build_tag'], dev['dockerfile']),
                         ('alpine', 'latest', 'latest.Dockerfile'))
        self.assertEqual((container['tag_repo'], container['dockerfile']), ('latest', 'latest.Dockerfile'))

    def test_missing_default_or_representative_is_not_replaced_silently(self):
        config = copy.deepcopy(self.config)
        del config['apps']['vlmcsd']
        for inputs in [{}, dict(targets='all', verify=True)]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                workflow_plan.plan(config, 'workflow_dispatch', {}, inputs, 'runner')
        self.assertEqual(workflow_plan.plan(config, 'workflow_dispatch', {},
                         dict(targets='aria2', verify=True), 'runner')['build_targets']['include'][0]['app_branch'], 'aria2')

    def test_catalog_target_id_collisions_fail_before_any_job_outputs(self):
        config = copy.deepcopy(self.config)
        config['apps']['runner-actions'] = copy.deepcopy(config['apps']['runner'])
        config['apps']['runner-actions']['targets'] = [{'tag': 'latest'}]
        with self.assertRaisesRegex(ValueError, 'duplicated catalog target_id'):
            workflow_plan.plan(config, 'workflow_dispatch', {}, {}, 'runner')

    def test_test_matrix_limit_remains_enforced(self):
        config = copy.deepcopy(self.config)
        config['apps']['vlmcsd']['platforms'] = ['linux/amd64'] * 257
        with self.assertRaisesRegex(ValueError, '256-job limit'):
            workflow_plan.plan(config, 'workflow_dispatch', {}, dict(verify=True), 'runner')

    def test_schedule_monitors_all_apps_with_unchanged_version_tag_policy(self):
        result = self.make('schedule', targets='aria2', verify=True)
        self.assertEqual(result['monitor'], 'true')
        self.assertEqual(result['build'], result['verify'])
        self.assertEqual(result['verify'], 'false')
        self.assertEqual(result['force_build'], 'false')
        self.assertEqual(len(result['build_targets']['include']), 30)
        versions = result['version_matrix']['include']
        self.assertEqual(len(versions), 24)
        self.assertEqual({t['app_branch'] for t in versions}, set(self.config['apps']))
        self.assertTrue(all(t['tag_repo'] == 'latest' for t in versions))

    def test_push_always_validates_without_starting_expensive_jobs(self):
        for message in ['ordinary update', '[full-build]', '[full-retest:runner:actions]']:
            with self.subTest(message=message):
                result = self.make('push', {'head_commit': {'message': message}}, targets='all', verify=True)
                self.assertTrue(all(result[k] == 'false' for k in ['build', 'verify', 'monitor', 'fetch_versions']))
                self.assertEqual(result['test_matrix'], {'include': []})

    def test_push_without_head_commit_still_only_validates(self):
        result = self.make('push', {'head_commit': None})
        self.assertEqual(result['build'], 'false')
        self.assertEqual(result['verify'], 'false')

    def test_commit_message_selectors_are_explicitly_retired(self):
        for message in ['[gpt-acceptance]', '[gpt-verification]', '[gpt-validate]',
                        '[gpt-dev:vlmcsd:latest]', '[gpt-container:vlmcsd:latest]',
                        '[gpt-retest:aria2:latest]', '[gpt-build:vlmcsd:latest]',
                        '[gpt-smoke:vlmcsd]', '[gpt-unknown]', '[gpt-']:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, 'Commit selectors are retired'):
                self.make('push', {'head_commit': {'message': message}})

    def test_retired_inputs_cannot_select_routes_or_override_configuration(self):
        for key, value in dict(execution_route='build', app_branch='aria2', tag_repo='latest', target_id='vlmcsd',
                               build_matrix='[]', platform='linux/amd64', force_build='false',
                               diagnostic_mode='version', layer_profile='base', image_name='alpine:latest',
                               dev_mode='build', version='1.0', revision='r1', custom_env='publish=true').items():
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'Only targets and verify'):
                self.make(**{key: value})

    def test_retired_external_events_remain_rejected(self):
        for event in ['pull_request', 'workflow_call', 'repository_dispatch', 'unknown']:
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.make(event)

    def test_inputs_must_be_an_object(self):
        for inputs in [None, [], 'targets=vlmcsd', False, 1]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                workflow_plan.plan(self.config, 'workflow_dispatch', {}, inputs, 'runner')

    def test_fixed_diagnostics_cover_stable_images_and_both_detail_architectures(self):
        result = self.make(verify=True)
        self.assertEqual(set(result['images']), {'debian:latest', 'ubuntu:latest', 'alpine:latest',
                                               'debian:sid', 'ubuntu:devel'})
        self.assertEqual({(r['image_name'], r['arch']) for r in result['image_platforms']},
                         {(image, arch) for image in result['images'] for arch in ['amd64', 'arm64']})

    def test_representative_eight_combinations_need_no_hardcoded_route(self):
        result = self.make(targets='aria2,samba:alpine,vlmcsd,runner:actions-slim', verify=True)
        self.assertEqual(len(result['test_matrix']['include']), 8)
        self.assertEqual({t['app'] for t in result['test_matrix']['include']}, {'aria2', 'samba', 'vlmcsd', 'runner'})

    def test_catalog_changes_flow_to_selected_target_and_representative(self):
        config = copy.deepcopy(self.config)
        target = next(t for t in config['apps']['samba']['targets'] if t['tag'] == 'alpine')
        target['base_image'], target['build_arg'] = 'example:changed', 'example-argument'
        result = workflow_plan.plan(config, 'workflow_dispatch', {},
                                    dict(targets='samba:alpine', verify=True), 'runner')
        for key in ['build_targets', 'dev_matrix']:
            row = result[key]['include'][0]
            self.assertEqual((row['base_image'], row['build_arg']), ('example:changed', 'example-argument'))

    def test_inputs_and_catalog_are_not_mutated(self):
        config, inputs = copy.deepcopy(self.config), dict(targets='novnc_alpine', verify=True)
        before = copy.deepcopy((config, inputs))
        workflow_plan.plan(config, 'workflow_dispatch', {}, inputs, 'runner')
        self.assertEqual((config, inputs), before)

    def test_publication_is_false_for_every_event_and_accepted_input(self):
        for event, inputs in [('push', {}), ('schedule', {}), ('workflow_dispatch', {}),
                              ('workflow_dispatch', dict(verify=True)),
                              ('workflow_dispatch', dict(targets='all', verify=True))]:
            with self.subTest(event=event, inputs=inputs):
                result = self.make(event, **inputs)
                self.assertEqual(result['publish'], 'false')
                self.assertEqual(result['may_publish'], 'false')
                self.assertNotIn('route', result)
                self.assertNotIn('dev_mode', result)

    def test_actual_cli_writes_typed_plan_without_publication_switch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event, output = root / 'event.json', root / 'output'
            event.write_text('{}', encoding='utf-8')
            for inputs, tests in [(dict(verify=False), 0), (dict(verify='true', targets='all'), 52)]:
                with self.subTest(inputs=inputs):
                    env = dict(GITHUB_EVENT_PATH=str(event), GITHUB_EVENT_NAME='workflow_dispatch',
                               WORKFLOW_INPUTS=json.dumps(inputs), WORKFLOW_READ_ONLY='false',
                               RUNNER_IMAGE='fixture', GITHUB_OUTPUT=str(output))
                    with mock.patch.dict(os.environ, env), mock.patch('builtins.print'):
                        workflow_plan.main()
                    values = dict(line.split('=', 1) for line in output.read_text().splitlines())
                    self.assertEqual(values['publish'], values['may_publish'])
                    self.assertEqual(values['publish'], 'false')
                    self.assertEqual(len(json.loads(values['test_matrix'])['include']), tests)
                    output.unlink()

    def test_actual_cli_rejects_retired_input_without_emitting_job_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            event, output = root / 'event.json', root / 'output'
            event.write_text('{}', encoding='utf-8')
            env = dict(GITHUB_EVENT_PATH=str(event), GITHUB_EVENT_NAME='workflow_dispatch',
                       WORKFLOW_INPUTS='{"execution_route":"production"}',
                       RUNNER_IMAGE='fixture', GITHUB_OUTPUT=str(output))
            with mock.patch.dict(os.environ, env), self.assertRaises(ValueError):
                workflow_plan.main()
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
