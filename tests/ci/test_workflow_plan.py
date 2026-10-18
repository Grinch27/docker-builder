#!/usr/bin/env python3
# Requirements: only unselected build defaults to vlmcsd; retired routes fail and selections stay catalog-only.
# Unknowns/research: live GitHub scheduling and registry publication require separate validation.
# Risks/verification: explicit selectors never fall back; full matrices, Dev comparison inputs and routing stay intact.
# Optimization: test the pure planner without Docker, network, or external writes.
"""Exercise event and target selection boundaries for the unified workflow."""

import copy
import json
from pathlib import Path
import unittest

import catalog
import workflow_plan


ROOT = Path(__file__).resolve().parents[2]


class WorkflowPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = catalog.catalog_from_readme(ROOT / "README.md")

    def make(self, route="validate", event_name="workflow_dispatch", event=None, **inputs):
        return workflow_plan.plan(self.config, event_name, event or {},
                                  dict(execution_route=route, **inputs), "resolved-runner")

    def test_all_push_requests_remain_nonpublishing(self):
        messages = ["ordinary update", "[full-build]", "[full-retest:runner:actions]",
                    "[smoke-vlmcsd]", "[probe-smoke]", "[smoke-target:samba-alpine]",
                    "[diagnostics-full]"]
        for route in workflow_plan.ROUTES:
            for message in messages:
                with self.subTest(route=route, message=message):
                    result = self.make(route, "push", {"head_commit": {"message": message},
                                      "client_payload": {"execution_route": "production"}})
                    self.assertEqual(result["publish"], "false")
                    self.assertEqual(result["may_publish"], "false")
                    self.assertNotIn(result["route"], {"production", "dev", "container", "build", "monitor"})

    def test_retired_external_events_are_rejected(self):
        for event in ['pull_request', 'workflow_call', 'repository_dispatch']:
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.make('production', event)

    def test_schedule_is_monitor_only(self):
        result = self.make('production', 'schedule')
        self.assertEqual(result['route'], 'monitor')
        self.assertEqual(result['publish'], 'false')
        self.assertEqual(result['may_publish'], 'false')

    def test_publishing_routes_cannot_be_selected(self):
        for route in ['production', 'container', 'promote-all']:
            with self.subTest(route=route), self.assertRaises(ValueError):
                self.make(route)

    def test_environment_flag_cannot_restore_publication(self):
        import os
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as directory:
            event = Path(directory) / 'event.json'
            event.write_text('{}', encoding='utf-8')
            output = Path(directory) / 'output'
            env = dict(GITHUB_EVENT_PATH=str(event), GITHUB_EVENT_NAME='workflow_dispatch',
                       WORKFLOW_INPUTS=json.dumps({'execution_route': 'production'}),
                       WORKFLOW_READ_ONLY='false', RUNNER_IMAGE='fixture', GITHUB_OUTPUT=str(output))
            with mock.patch.dict(os.environ, env), self.assertRaisesRegex(ValueError, 'prohibited execution_route'):
                workflow_plan.main()
            self.assertFalse(output.exists())

    def test_full_matrix_is_derived_from_all_configured_platforms(self):
        result = self.make("test")
        expected = {(app, target["tag"], platform) for app, meta in self.config["apps"].items()
                    for target in meta["targets"] for platform in meta["platforms"]}
        actual = {(row["app"], row["tag"], row["platform"]) for row in result["test_matrix"]["include"]}
        self.assertEqual(actual, expected)
        self.assertTrue(all(t["runner_image"] == "resolved-runner"
                            for t in result["build_targets"]["include"]))

    def test_retest_selects_target_and_configured_platforms(self):
        result = self.make(event_name="push", event={"head_commit": {"message": "fix [gpt-retest:runner:actions]"}})
        self.assertEqual({(t["app"], t["tag"]) for t in result["test_matrix"]["include"]}, {("runner", "actions")})

    def test_target_and_platform_selection(self):
        result = self.make("test", target_id="samba-alpine", platform="linux/arm64")
        self.assertEqual(result["test_matrix"]["include"], [{"app": "samba", "tag": "alpine", "platform": "linux/arm64"}])

    def test_unknown_and_ambiguous_selections_fail(self):
        cases = [dict(app_branch="../runner"), dict(app_branch="missing"), dict(tag_repo="missing"),
                 dict(target_id="missing"), dict(app_branch="runner", target_id="samba-alpine"),
                 dict(app_branch="runner", platform="linux/riscv64")]
        for inputs in cases:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                self.make("test", **inputs)

    def test_invalid_or_unknown_inputs_fail(self):
        for inputs in [dict(force_build="yes"), dict(dev_mode="unsafe"), dict(diagnostic_mode="unknown"),
                       dict(layer_profile="unknown"), dict(app_branch="runner\nother"),
                       dict(build_matrix=5), dict(image_name="alpine:latest;id")]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                self.make(**inputs)
        with self.assertRaises(ValueError):
            self.make("unknown")

    def test_malformed_commit_selectors_fail(self):
        for message in ["[gpt-retest:runner]", "[gpt-smoke:../runner]"]:
            with self.subTest(message=message), self.assertRaises(ValueError):
                self.make(event_name="push", event={"head_commit": {"message": message}})

    def test_matrix_rejects_unknown_duplicate_and_malformed_entries(self):
        bad = ["{}", "[]", '[null]', '{"include":{}}',
               '[{"app_branch":"missing"}]', '[{"app_branch":"aria2","runner_image":"custom"}]',
               '[{"app_branch":"aria2"},{"app_branch":"aria2"}]',
               '[{"app_branch":"aria2","custom_env":"bad\\nvalue"}]']
        for matrix in bad:
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                self.make("build", build_matrix=matrix)

    def test_matrix_supports_formatted_json_and_preserves_order(self):
        rows = [{"app_branch": "samba", "tag_repo": "alpine"}, {"app_branch": "runner", "tag_repo": "actions"}]
        result = self.make("monitor", build_matrix=json.dumps({"include": rows}, indent=2))
        self.assertEqual([t["target_id"] for t in result["build_targets"]["include"]], ["samba-alpine", "runner-actions"])
        self.assertEqual(result["publish"], "false")
        with self.assertRaises(ValueError):
            self.make("build", app_branch="samba", build_matrix=json.dumps(rows))

    def test_dev_container_acceptance_requires_single_target(self):
        for route in ['dev-verify', 'container-verify']:
            with self.subTest(route=route), self.assertRaises(ValueError):
                self.make(route, app_branch='runner')
            self.assertEqual(len(self.make(route, app_branch='runner', tag_repo='actions')['build_targets']['include']), 1)

    def test_retired_smoke_routes_and_selectors_fail(self):
        for route in ['smoke', 'registry-smoke']:
            for inputs in [{}, {'target_id': 'vlmcsd'}]:
                with self.subTest(route=route, inputs=inputs), self.assertRaises(ValueError):
                    self.make(route, **inputs)
        for message in ['[gpt-smoke:vlmcsd]', '[gpt-smoke:runner-actions]']:
            with self.subTest(message=message), self.assertRaises(ValueError):
                self.make(event_name='push', event={'head_commit': {'message': message}})

    def test_dev_promotion_and_retired_smoke_mode_are_rejected(self):
        for mode in ['auto', 'build', 'smoke-target', 'promote-dockerhub', 'promote-ghcr', 'promote-all']:
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                self.make('dev', dev_mode=mode, target_id='runner-actions', version='1.0', revision='r1-a1')

    def test_dev_defaults_preserve_exclusions_and_alpine_destination(self):
        result = self.make("dev", dev_mode="preflight")
        targets = result["dev_matrix"]["include"]
        self.assertFalse({t["app_branch"] for t in targets} & workflow_plan.DEV_EXCLUDED)
        self.assertEqual(next(t["tag_repo"] for t in targets if t["app_branch"] == "novnc_alpine"), "alpine")
        production = self.make("test")["build_targets"]["include"]
        self.assertEqual(next(t["tag_repo"] for t in production if t["app_branch"] == "novnc_alpine"), "latest")
        dev = next(t for t in targets if t['app_branch'] == 'novnc_alpine')
        self.assertEqual(dev['build_tag'], 'latest')
        self.assertEqual(dev['dockerfile'], 'latest.Dockerfile')

    def test_diagnostics_modes_do_not_run_monitor(self):
        for mode in ["version", "layers", "both", "all-platforms"]:
            with self.subTest(mode=mode):
                result = self.make("diagnostics", diagnostic_mode=mode, image_name="alpine:latest")
                self.assertEqual(result["route"], "diagnostics")
                self.assertEqual(result["images"], ["alpine:latest"])
                self.assertEqual(result["fetch_versions"], str(mode in {"version", "both"}).lower())
                self.assertEqual(result["version_matrix"]["include"][0]["app_branch"], "vlmcsd")

    def test_config_changes_flow_to_target_settings(self):
        config = copy.deepcopy(self.config)
        config["apps"]["runner"]["targets"][2]["base_image"] = "example:changed"
        result = workflow_plan.plan(config, "workflow_dispatch", {}, {"execution_route": "test"}, "runner")
        expected = catalog.get(config, "runner", config["apps"]["runner"]["targets"][2]["tag"])
        actual = next(t for t in result["build_targets"]["include"] if t["app_branch"] == "runner" and t["tag_repo"] == expected["tag_repo"])
        self.assertEqual(actual["base_image"], "example:changed")

    def test_staging_rejects_all_publishing_routes(self):
        for inputs in [dict(execution_route="production"), dict(execution_route="container"),
                       dict(execution_route="dev", dev_mode="auto"),
                       dict(execution_route="dev", dev_mode="build"),
                       dict(execution_route="dev", dev_mode="promote-all")]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                workflow_plan.plan(self.config, "workflow_dispatch", {}, inputs, "runner")

    def test_staging_rejects_automatic_and_external_write_entrypoints(self):
        scheduled = workflow_plan.plan(self.config, "schedule", {}, {}, "runner")
        self.assertEqual(scheduled["route"], "monitor")
        self.assertEqual(scheduled["fetch_versions"], "true")
        self.assertEqual(scheduled["publish"], "false")
        self.assertEqual(scheduled["may_publish"], "false")
        for event_name in ["repository_dispatch", "workflow_call"]:
            with self.subTest(event=event_name), self.assertRaises(ValueError):
                workflow_plan.plan(self.config, event_name, {}, {}, "runner")

    def test_staging_verifies_real_representative_paths(self):
        result = workflow_plan.plan(self.config, "push", {"head_commit": {
            "message": "workflow regression [gpt-verification]"}}, {}, "runner")
        self.assertEqual(result["route"], "verification")
        self.assertEqual(result["publish"], "false")
        self.assertEqual(result["may_publish"], "false")
        self.assertEqual(result["force_build"], "true")
        self.assertEqual({t["app_branch"] for t in result["build_targets"]["include"]}, {"vlmcsd"})
        self.assertEqual({t["app"] for t in result["test_matrix"]["include"]}, {"aria2", "samba", "vlmcsd", "runner"})
        self.assertEqual(result["images"], ["alpine:latest"])

    def test_ordinary_staging_push_only_validates(self):
        for message in ["ordinary update", "[full-build]", "[gpt-validate]"]:
            with self.subTest(message=message):
                result = workflow_plan.plan(self.config, "push", {"head_commit": {
                    "message": message}}, {"execution_route": "acceptance"}, "runner")
                self.assertEqual(result["route"], "validate")
                self.assertEqual(result["fetch_versions"], "false")
                self.assertEqual(result["publish"], "false")
                self.assertEqual(result["may_publish"], "false")

    def test_dispatch_keeps_explicit_verification_and_full_coverage(self):
        for inputs in [{}, {"execution_route": "verification"}]:
            result = workflow_plan.plan(self.config, "workflow_dispatch", {}, inputs, "runner")
            self.assertEqual(result["route"], "verification")
            self.assertEqual(len(result["test_matrix"]["include"]), 8)
        result = workflow_plan.plan(self.config, "push", {"head_commit": {
            "message": "[gpt-acceptance]"}}, {}, "runner")
        self.assertEqual(result["route"], "acceptance")
        self.assertEqual(len(result["test_matrix"]["include"]), 52)

    def test_staging_unknown_malformed_and_multiple_selectors_fail(self):
        for message in ["[gpt-verification] [gpt-retest:aria2:latest]", "[gpt-verification:aria2]",
                        "[gpt-acceptance:aria2]", "[gpt-dev:bad]", "[gpt-unknown]",
                        "[gpt-retest:aria2:latest", "[gpt-validate] [gpt-",
                        "[gpt-verification] [gpt-verification]"]:
            with self.subTest(message=message), self.assertRaises(ValueError):
                workflow_plan.plan(self.config, "push", {"head_commit": {
                    "message": message}}, {}, "runner")

    def test_staging_target_build_is_forced_and_nonpublishing(self):
        result = workflow_plan.plan(self.config, "push",
                   {"head_commit": {"message": "fix [gpt-build:vlmcsd:latest]"}}, {}, "runner")
        self.assertEqual(result["route"], "build")
        self.assertEqual(result["force_build"], "true")
        self.assertEqual(result["may_publish"], "false")
        self.assertEqual(len(result["build_targets"]["include"]), 1)

    def test_manual_single_target_build_replaces_fixed_registry_smoke(self):
        for app, tag in [("samba", "alpine"), ("aria2", "latest"), ("runner", "actions")]:
            with self.subTest(app=app, tag=tag):
                result = workflow_plan.plan(
                    self.config, "workflow_dispatch", {},
                    {"execution_route": "build", "app_branch": app, "tag_repo": tag}, "runner")
                self.assertEqual(result["route"], "build")
                self.assertEqual(result["force_build"], "true")
                self.assertEqual(result["fetch_versions"], "true")
                self.assertEqual(result["publish"], "false")
                self.assertEqual(result["may_publish"], "false")
                self.assertEqual([(t["app_branch"], t["tag_repo"]) for t in
                                  result["build_targets"]["include"]], [(app, tag)])
        with self.assertRaises(ValueError):
            workflow_plan.plan(self.config, "workflow_dispatch", {},
                                       {"execution_route": "registry-smoke"}, "runner")

    def test_unselected_build_matches_explicit_vlmcsd_plan(self):
        for inputs in [{}, dict(app_branch='', tag_repo='', target_id='', build_matrix=''),
                       dict(force_build='false', custom_env='EXAMPLE=value')]:
            with self.subTest(inputs=inputs):
                actual = self.make('build', **inputs)
                explicit = dict(inputs, app_branch='vlmcsd', tag_repo='latest')
                self.assertEqual(actual, self.make('build', **explicit))
                self.assertEqual(actual['target_id'], 'vlmcsd')
                self.assertEqual(actual['force_build'], 'true')
                self.assertEqual(actual['fetch_versions'], 'true')
                self.assertEqual({row['platform'] for row in actual['test_matrix']['include']},
                                 {'linux/amd64', 'linux/arm64', 'linux/386'})
                self.assertEqual(actual['publish'], 'false')
                self.assertEqual(actual['may_publish'], 'false')

    def test_explicit_build_selectors_override_default(self):
        cases = [(dict(app_branch='aria2'), 'aria2'),
                 (dict(app_branch='samba', tag_repo='alpine'), 'samba-alpine'),
                 (dict(tag_repo='beta'), 'adguardvpn-cli-beta'),
                 (dict(target_id='runner-actions'), 'runner-actions'),
                 (dict(build_matrix='[{"app_branch":"runner","tag_repo":"slim"}]'), 'runner-slim')]
        for inputs, expected in cases:
            with self.subTest(inputs=inputs):
                result = self.make('build', **inputs)
                self.assertEqual([row['target_id'] for row in result['build_targets']['include']], [expected])

    def test_explicit_invalid_or_ambiguous_build_does_not_fall_back(self):
        for inputs in [dict(app_branch='missing'), dict(app_branch='runner'), dict(tag_repo='latest'),
                       dict(tag_repo='missing'), dict(target_id='missing'),
                       dict(app_branch='aria2', target_id='vlmcsd'),
                       dict(build_matrix='[{"app_branch":"aria2"},{"app_branch":"vlmcsd"}]')]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                self.make('build', **inputs)
        config = copy.deepcopy(self.config)
        del config['apps']['vlmcsd']
        with self.assertRaises(ValueError):
            workflow_plan.plan(config, 'workflow_dispatch', {}, {'execution_route': 'build'}, 'runner')

    def test_build_default_does_not_filter_monitor_test_or_acceptance(self):
        monitor = self.make('monitor')
        self.assertEqual(len(monitor['build_targets']['include']), 30)
        self.assertEqual(len(monitor['version_matrix']['include']), 24)
        for route in ['test', 'acceptance']:
            with self.subTest(route=route):
                matrix = self.make(route)['test_matrix']['include']
                self.assertEqual(len(matrix), 52)
                self.assertEqual(len({row['app'] for row in matrix}), 24)

    def test_full_acceptance_covers_catalog_and_isolates_compatibility_jobs(self):
        result = workflow_plan.plan(self.config, "push",
                   {"head_commit": {"message": "ci: full acceptance [gpt-acceptance]"}}, {}, "runner")
        expected = {(app, target["tag"], platform) for app, meta in self.config["apps"].items()
                    for target in meta["targets"] for platform in meta["platforms"]}
        actual = {(row["app"], row["tag"], row["platform"]) for row in result["test_matrix"]["include"]}
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), 52)
        self.assertEqual(result["route"], "acceptance")
        self.assertEqual(result["dev_mode"], "build")
        self.assertEqual(result["publish"], "false")
        self.assertEqual(result["may_publish"], "false")
        self.assertEqual(result["fetch_versions"], "false")
        self.assertEqual(result["force_build"], "true")
        for matrix in ["dev_matrix", "build_targets"]:
            self.assertEqual([t["target_id"] for t in result[matrix]["include"]], ["vlmcsd"])

    def test_acceptance_filters_and_multiple_push_selectors_fail(self):
        for route, inputs in [("acceptance", dict(app_branch="aria2")),
                              ("acceptance", dict(platform="linux/amd64")),
                              ("dev-verify", dict(platform="linux/amd64")),
                              ("container-verify", dict(custom_env="arch_branch=linux/amd64")),
                              ("dev-verify", dict(app_branch="runner"))]:
            with self.subTest(route=route, inputs=inputs), self.assertRaises(ValueError):
                workflow_plan.plan(self.config, "workflow_dispatch", {},
                                          dict(execution_route=route, **inputs), "runner")
        with self.assertRaises(ValueError):
            workflow_plan.plan(self.config, "push", {"head_commit": {
                "message": "[gpt-acceptance] [gpt-retest:aria2:latest]"}}, {}, "runner")

    def test_dev_container_and_retest_push_routes_remain_nonpublishing(self):
        for selector, route in [("gpt-dev", "dev-verify"), ("gpt-container", "container-verify"),
                                ("gpt-retest", "test")]:
            with self.subTest(selector=selector):
                result = workflow_plan.plan(self.config, "push", {"head_commit": {
                    "message": "test [" + selector + ":vlmcsd:latest]"}}, {}, "runner")
                self.assertEqual(result["route"], route)
                self.assertEqual(result["publish"], "false")
                self.assertEqual(result["may_publish"], "false")
                self.assertEqual(len(result["test_matrix"]["include"]), 3)
        result = workflow_plan.plan(self.config, "workflow_dispatch", {},
                                            dict(execution_route="dev-verify", target_id="novnc_alpine"), "runner")
        self.assertEqual(result["dev_matrix"]["include"][0]["tag_repo"], "alpine")

    def test_staging_retest_list_selects_only_configured_targets(self):
        result = workflow_plan.plan(self.config, "push", {"head_commit": {
            "message": "repair [gpt-retest:ffmpeg:latest,sdnext:latest]"}}, {}, "runner")
        self.assertEqual(result['route'], 'test')
        self.assertEqual({(r['app'], r['tag']) for r in result['test_matrix']['include']},
                         {('ffmpeg', 'latest'), ('sdnext', 'latest')})
        self.assertEqual(result['publish'], 'false')
        self.assertEqual(result['may_publish'], 'false')
        for suffix in ['ffmpeg', 'ffmpeg:latest,', '../ffmpeg:latest',
                       'ffmpeg:latest,ffmpeg:latest', 'missing:latest']:
            with self.subTest(selector=suffix), self.assertRaises(ValueError):
                workflow_plan.plan(self.config, 'push', {'head_commit': {
                    'message': '[gpt-retest:' + suffix + ']'}}, {}, 'runner')


if __name__ == "__main__":
    unittest.main()
