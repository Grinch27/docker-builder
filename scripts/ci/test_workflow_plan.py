#!/usr/bin/env python3
# Requirements: push/PR cannot publish; selections must refer to configured targets/platforms.
# Unknowns/research: live GitHub scheduling and registry publication require separate validation.
# Risks/verification: malformed selectors, duplicate matrices, Dev tag compatibility, routing isolation.
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
                    "[diagnostics-full]", "ci: smoke catalog build"]
        for route in workflow_plan.ROUTES:
            for message in messages:
                with self.subTest(route=route, message=message):
                    result = self.make(route, "push", {"head_commit": {"message": message},
                                      "client_payload": {"execution_route": "production"}})
                    self.assertEqual(result["publish"], "false")
                    self.assertEqual(result["may_publish"], "false")
                    self.assertNotIn(result["route"], {"production", "dev", "container", "build", "monitor"})

    def test_pr_ignores_commit_and_payload_routes(self):
        result = self.make("production", "pull_request", {"head_commit": {"message": "[full-build]"}})
        self.assertEqual(result["route"], "validate")
        self.assertEqual(result["publish"], "false")

    def test_schedule_preserves_production(self):
        self.assertEqual(self.make("validate", "schedule")["route"], "production")

    def test_repository_dispatch_default_and_explicit_routes(self):
        for route in ["production", "monitor", "test"]:
            result = workflow_plan.plan(self.config, "repository_dispatch",
                                       {"client_payload": {"execution_route": route}}, {}, "runner")
            self.assertEqual(result["route"], route)
        result = workflow_plan.plan(self.config, "repository_dispatch", {}, {}, "runner")
        self.assertEqual(result["route"], "production")

    def test_full_matrix_is_derived_from_all_configured_platforms(self):
        result = self.make("test")
        expected = {(app, target["tag"], platform) for app, meta in self.config["apps"].items()
                    for target in meta["targets"] for platform in meta["platforms"]}
        actual = {(row["app"], row["tag"], row["platform"]) for row in result["test_matrix"]["include"]}
        self.assertEqual(actual, expected)
        self.assertTrue(all(t["runner_image"] == "resolved-runner"
                            for t in result["build_targets"]["include"]))

    def test_retest_selects_target_and_configured_platforms(self):
        result = self.make(event_name="push", event={"head_commit": {"message": "fix [full-retest:runner:actions]"}})
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
        for message in ["[full-retest:runner]", "[smoke-target:../runner]"]:
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
        result = self.make("build", build_matrix=json.dumps({"include": rows}, indent=2))
        self.assertEqual([t["target_id"] for t in result["build_targets"]["include"]], ["samba-alpine", "runner-actions"])
        self.assertEqual(result["publish"], "false")
        with self.assertRaises(ValueError):
            self.make("build", app_branch="samba", build_matrix=json.dumps(rows))

    def test_container_requires_a_single_target(self):
        with self.assertRaises(ValueError):
            self.make("container")
        self.assertEqual(len(self.make("container", app_branch="runner", tag_repo="actions")["build_targets"]["include"]), 1)

    def test_smoke_and_promotion_require_concrete_targets(self):
        with self.assertRaises(ValueError):
            self.make("smoke")
        self.assertEqual(self.make("smoke", target_id="runner-actions")["dev_mode"], "smoke-target")
        for inputs in [{}, dict(target_id="runner-actions"), dict(target_id="runner-actions", version="1.0")]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                self.make("dev", dev_mode="promote-all", **inputs)
        result = self.make("dev", dev_mode="promote-all", target_id="runner-actions", version="1.0", revision="r1-a1")
        self.assertEqual(result["dev_mode"], "promote-all")

    def test_dev_defaults_preserve_exclusions_and_alpine_destination(self):
        result = self.make("dev", dev_mode="auto")
        targets = result["dev_matrix"]["include"]
        self.assertFalse({t["app_branch"] for t in targets} & workflow_plan.DEV_EXCLUDED)
        self.assertEqual(next(t["tag_repo"] for t in targets if t["app_branch"] == "novnc_alpine"), "alpine")
        production = self.make("production")["build_targets"]["include"]
        self.assertEqual(next(t["tag_repo"] for t in production if t["app_branch"] == "novnc_alpine"), "latest")

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
                workflow_plan.staging_plan(self.config, "workflow_dispatch", {}, inputs, "runner")

    def test_staging_rejects_automatic_and_external_write_entrypoints(self):
        for event_name in ["schedule", "repository_dispatch", "workflow_call"]:
            with self.subTest(event=event_name), self.assertRaises(ValueError):
                workflow_plan.staging_plan(self.config, event_name, {}, {}, "runner")

    def test_staging_verifies_real_representative_paths(self):
        result = workflow_plan.staging_plan(self.config, "push", {}, {}, "runner")
        self.assertEqual(result["route"], "verification")
        self.assertEqual(result["publish"], "false")
        self.assertEqual(result["may_publish"], "false")
        self.assertEqual(result["force_build"], "true")
        self.assertEqual({t["app_branch"] for t in result["build_targets"]["include"]}, {"vlmcsd"})
        self.assertEqual({t["app"] for t in result["test_matrix"]["include"]}, {"aria2", "samba", "vlmcsd", "runner"})
        self.assertEqual(result["images"], ["alpine:latest"])

    def test_staging_target_build_is_forced_and_nonpublishing(self):
        result = workflow_plan.staging_plan(self.config, "push",
                   {"head_commit": {"message": "fix [gpt-build:vlmcsd:latest]"}}, {}, "runner")
        self.assertEqual(result["route"], "build")
        self.assertEqual(result["force_build"], "true")
        self.assertEqual(result["may_publish"], "false")
        self.assertEqual(len(result["build_targets"]["include"]), 1)


if __name__ == "__main__":
    unittest.main()
