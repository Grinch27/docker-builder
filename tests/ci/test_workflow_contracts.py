#!/usr/bin/env python3
# Requirements: two inputs, fixed combined diagnostics and nonpublishing acceptance must fail closed.
# Unknowns/research: GitHub-hosted execution and registry publication remain unverified locally.
# Risks/verification: execute real check/diagnostic gates; reject missing evidence, ignored tests and retired controls.
# Optimization: one standard-library graph/contract gate; actionlint validates YAML separately.
"""Verify failure boundaries and executable shell in the single core workflow."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[2]
TEXT = (ROOT / ".github/workflows/gpt_dev.yml").read_text(encoding="utf-8")
def job_blocks(text):
    body = text.split("\njobs:\n", 1)[1]
    matches = list(re.finditer(r"^  ([a-zA-Z0-9_-]+):\s*$", body, re.MULTILINE))
    return {m[1]: body[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(body)]
            for i, m in enumerate(matches)}


def dependencies(block):
    single = re.search(r"^    needs: ([a-zA-Z0-9_-]+)$", block, re.MULTILINE)
    if single:
        return {single[1]}
    multiple = re.search(r"^    needs:\n((?:    - [a-zA-Z0-9_-]+\n)+)", block, re.MULTILINE)
    return set(re.findall(r"    - ([a-zA-Z0-9_-]+)", multiple[1])) if multiple else set()


def validate_workflow(root):
    flow = root / ".github/workflows"
    files = {p.name for p in flow.glob("*.y*ml")}
    expected = {"gpt_dev.yml", "download_artifact.yml"}
    assert files == expected, f"Expected exactly two workflows, got {sorted(files)}"
    for path in flow.glob("*.y*ml"):
        for ref in re.findall(r"uses:\s+\./\.github/workflows/([a-zA-Z0-9_.-]+\.yml)", path.read_text(encoding="utf-8")):
            assert ref in expected, f"Dangling reusable workflow reference: {path.name} -> {ref}"
    assert "  pull-image:" in (flow / "download_artifact.yml").read_text(encoding="utf-8"), "Manual Docker pull route missing"
    text = (flow / "gpt_dev.yml").read_text(encoding="utf-8")
    blocks = job_blocks(text)
    required = {"runner-image", "plan", "fetch-versions", "monitor", "check", "build",
                "dev-inspect", "dev-build", "test-images",
                "diagnostic-layers", "diagnostic-platforms", "diagnostic-collect",
                "diagnostic-meta-platforms", "diagnostic-validate", "container-build"}
    assert required <= blocks.keys(), "Core capability Job missing"
    planning = blocks["plan"]
    outputs = set(re.findall(r"^      ([a-zA-Z0-9_-]+): \$\{\{ steps\.plan\.outputs\.", planning, re.MULTILINE))
    references = set(re.findall(r"needs\.plan\.outputs\.([a-zA-Z0-9_-]+)", text))
    assert references <= outputs, "Missing plan outputs: " + str(references - outputs)
    gate = planning.find("python3 -m unittest discover")
    command = planning.find("python3 scripts/ci/workflow_plan.py")
    assert 0 <= gate < command, "Validation must run before planning"
    assert "continue-on-error:" not in planning, "Planning validation must fail closed"
    edges = {key: dependencies(block) for key, block in blocks.items()}
    for key, block in blocks.items():
        assert not re.search(r"^    uses:", block, re.MULTILINE), "Nested workflow remains: " + key
        assert edges[key] <= blocks.keys(), "Dangling needs for " + key
        references = set(re.findall(r"needs\.([a-zA-Z0-9_-]+)\.", block))
        assert references <= edges[key], "Undeclared needs for " + key + ": " + str(references - edges[key])
    visiting, visited = set(), set()

    def visit(key):
        assert key not in visiting, "Job dependency cycle: " + key
        if key in visited:
            return
        visiting.add(key)
        for parent in edges[key]:
            visit(parent)
        visiting.remove(key)
        visited.add(key)

    for key in blocks:
        visit(key)
    print(f"Unified Job graph: PASS ({len(blocks)} Jobs, 2 workflows total)")



def script_for(job, name):
    block = job_blocks(TEXT)[job]
    step = block.split("    - name: " + name + "\n", 1)[1].split("    - name:", 1)[0]
    match = re.search(r"^      run: (?:&[\w-]+ )?\|[-+]?\n((?:        [^\n]*\n|\n)*)", step, re.MULTILINE)
    if not match:
        raise ValueError("Missing literal shell for " + name)
    return textwrap.dedent(match[1])


class WorkflowContractTests(unittest.TestCase):
    def test_manual_workflow_rejects_dangling_reusable_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            flow = root / '.github/workflows'
            flow.mkdir(parents=True)
            (flow / 'gpt_dev.yml').write_text(TEXT, encoding='utf-8')
            (flow / 'download_artifact.yml').write_text(
                'jobs:\n  pull-image:\n    uses: ./.github/workflows/retired.yml\n', encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, 'Dangling reusable'):
                validate_workflow(root)

    def test_job_graph_has_no_dangling_or_nested_calls(self):
        validate_workflow(ROOT)

    def test_only_targets_and_verify_are_public_inputs(self):
        inputs = TEXT.split('  workflow_dispatch:\n    inputs:\n', 1)[1].split('\npermissions:', 1)[0]
        self.assertEqual(set(re.findall(r'^      ([a-z_]+):', inputs, re.MULTILINE)), {'targets', 'verify'})
        self.assertIn('        default: vlmcsd', inputs)
        self.assertIn('        type: boolean\n        default: false', inputs)
        for control in ['execution_route', 'needs.plan.outputs.route', 'diagnostic_mode', 'layer_profile']:
            self.assertNotIn(control, TEXT)

    def test_acceptance_jobs_use_the_same_strict_verify_gate(self):
        jobs = job_blocks(TEXT)
        for name in ['dev-inspect', 'dev-build', 'container-build', 'test-images',
                     'diagnostic-layers', 'diagnostic-platforms', 'diagnostic-collect',
                     'diagnostic-meta-platforms', 'diagnostic-validate']:
            with self.subTest(job=name):
                condition = re.search(r'^    if: (.*)$', jobs[name], re.MULTILINE)[1]
                self.assertIn("needs.plan.outputs.verify == 'true'", condition)
        self.assertIn('diagnostic-meta-platforms', dependencies(jobs['diagnostic-validate']))

    def test_graph_rejects_undeclared_plan_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            flow = root / '.github/workflows'
            flow.mkdir(parents=True)
            (flow / 'gpt_dev.yml').write_text(TEXT.replace('needs.plan.outputs.verify', 'needs.plan.outputs.retired'), encoding='utf-8')
            (flow / 'download_artifact.yml').write_text('jobs:\n  pull-image:\n', encoding='utf-8')
            with self.assertRaisesRegex(AssertionError, 'Missing plan outputs'):
                validate_workflow(root)

    def diagnostic_result(self, mutate=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            version = 'app-version-vlmcsd/version-vlmcsd.json'
            meta = 'meta-platforms-vlmcsd-latest-a1/platforms.json'
            files = {
                version: dict(app_branch='vlmcsd', tag_repo='latest', status='success', version='1.0'),
                meta: dict(app='vlmcsd', tag='latest', platforms=[dict(platform=p, version='1.0')
                           for p in ['linux/amd64', 'linux/arm64', 'linux/386']]),
                'diagnostics-layer-summary/base_layers.json': {'alpine:latest': ['sha256:a']},
                'diagnostics-layer-summary/aggregated_layers.json': {'Layers': ['sha256:a']},
            }
            for arch in ['amd64', 'arm64']:
                files['layers-alpine-' + arch + '/layers.json'] = ['sha256:a']
                files['layer-info-alpine-' + arch + '/image_alpine.json'] = dict(
                    image='alpine:latest', architecture=arch, raw_data={'Layers': ['sha256:a']})
            needs = {key: {'result': 'success'} for key in ['fetch-versions', 'diagnostic-layers',
                     'diagnostic-platforms', 'diagnostic-collect', 'diagnostic-meta-platforms']}
            if mutate:
                mutate(files, needs)
            for name, data in files.items():
                path = root / 'diagnostic-contracts' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data), encoding='utf-8')
            env = dict(os.environ, RUNNER_TEMP=directory, DIAGNOSTIC_IMAGES='["alpine:latest"]',
                       META_TARGET=json.dumps(dict(app_branch='vlmcsd', build_tag='latest',
                         arch_branch='linux/amd64,linux/arm64,linux/386')), JOB_RESULTS=json.dumps(needs))
            return subprocess.run(['bash', '-e', '-o', 'pipefail'], env=env, capture_output=True, text=True,
                                  input=script_for('diagnostic-validate', 'Check selected diagnostic contracts'))

    def test_real_fixed_diagnostic_gate_accepts_complete_evidence(self):
        result = self.diagnostic_result()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('meta-app PASS', result.stdout)

    def test_real_fixed_diagnostic_gate_rejects_missing_or_incorrect_evidence(self):
        version = 'app-version-vlmcsd/version-vlmcsd.json'
        meta = 'meta-platforms-vlmcsd-latest-a1/platforms.json'
        detail = 'layer-info-alpine-arm64/image_alpine.json'
        cases = {
            'missing meta': lambda f, n: f.pop(meta),
            'wrong target': lambda f, n: f[meta].update(app='aria2'),
            'missing platform': lambda f, n: f[meta]['platforms'].pop(),
            'duplicate platform': lambda f, n: f[meta]['platforms'][1].update(platform='linux/amd64'),
            'unknown platform version': lambda f, n: f[meta]['platforms'][0].update(version='unknown'),
            'failed version probe': lambda f, n: f[version].update(status='probe_failed'),
            'unknown version': lambda f, n: f[version].update(version='unknown'),
            'padded unknown version': lambda f, n: f[version].update(version=' UNKNOWN '),
            'wrong version tag': lambda f, n: f[version].update(tag_repo='other'),
            'missing detailed architecture': lambda f, n: f.pop(detail),
            'duplicated detailed architecture': lambda f, n: f[detail].update(architecture='amd64'),
            'empty detailed layers': lambda f, n: f[detail]['raw_data'].update(Layers=[]),
            'missing image layers': lambda f, n: f['diagnostics-layer-summary/base_layers.json'].clear(),
        }
        for case, mutate in cases.items():
            with self.subTest(case=case):
                self.assertNotEqual(self.diagnostic_result(mutate).returncode, 0)

    def test_real_fixed_diagnostic_gate_rejects_failed_or_skipped_jobs(self):
        for job in ['fetch-versions', 'diagnostic-layers', 'diagnostic-platforms',
                    'diagnostic-collect', 'diagnostic-meta-platforms']:
            for status in ['failure', 'cancelled', 'skipped']:
                with self.subTest(job=job, status=status):
                    result = self.diagnostic_result(lambda f, n: n[job].update(result=status))
                    self.assertNotEqual(result.returncode, 0)

    def test_real_diagnostic_meta_pipeline_does_not_hide_probe_failure(self):
        script = script_for('diagnostic-meta-platforms', '(MetaData) ${{ env.app_branch }} in Container')
        values = {'env.category': 'platforms', 'env.arch_branch': 'linux/amd64',
                  'env.base_image': 'example:test', 'env.container_name': 'fixture', 'env.dir_container': '/tmp'}
        script = re.sub(r'\$\{\{ (.*?) \}\}', lambda match: values[match[1]], script)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work, tools = root / 'vlmcsd', root / 'bin'
            (work / 'meta-app').mkdir(parents=True)
            (work / 'meta-app/probe.sh').write_text('echo version=1.0\n', encoding='utf-8')
            tools.mkdir()
            for name, source in {
                'docker': '#!/bin/sh\nif [ "$1" = exec ] && [ "$3" = sh ]; then exit 7; fi\nexit 0\n',
                'python3': '#!/bin/sh\nexit 0\n',
            }.items():
                tool = tools / name
                tool.write_text(source, encoding='utf-8')
                tool.chmod(0o755)
            env = dict(os.environ, PATH=str(tools) + ':' + os.environ['PATH'], RUNNER_TEMP=directory,
                       GITHUB_WORKSPACE=str(ROOT), GITHUB_OUTPUT=str(root / 'output'),
                       container_name='fixture', app_branch='vlmcsd', tag_repo='latest')
            result = subprocess.run(['bash'], input=script, env=env, cwd=work, capture_output=True, text=True)
            self.assertEqual(result.returncode, 7, result.stderr)
            self.assertFalse((root / 'output').exists(), 'Failed meta probe emitted success')
            self.assertFalse((root / 'meta-platforms/platforms.json').exists())

    def test_planning_rejects_missing_or_ignored_validation(self):
        for source in [TEXT.replace("python3 -m unittest discover", "echo skipped tests"),
                       TEXT.replace("  plan:\n", "  plan:\n    continue-on-error: true\n", 1)]:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                workflows = root / ".github/workflows"
                workflows.mkdir(parents=True)
                (workflows / "gpt_dev.yml").write_text(source, encoding="utf-8")
                (workflows / "download_artifact.yml").write_text("jobs:\n  pull-image:\n", encoding="utf-8")
                with self.assertRaises(AssertionError):
                    validate_workflow(root)

    def test_all_inline_shell_parses(self):
        scripts = re.findall(r"^      run: (?:&[\w-]+ )?\|[-+]?\n((?:        [^\n]*\n|\n)*)", TEXT, re.MULTILINE)
        self.assertGreater(len(scripts), 30)
        for index, script in enumerate(scripts):
            # GitHub expands contexts before invoking Bash; use a harmless token for syntax checks.
            script = re.sub(r"\$\{\{.*?\}\}", "CONTEXT", textwrap.dedent(script))
            with self.subTest(script=index):
                result = subprocess.run(["bash", "-n"], input=script, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def check_result(self, data):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "docker-check").mkdir()
            if data is not None:
                (root / "docker-check/result.json").write_text(json.dumps(data), encoding="utf-8")
            env = dict(os.environ, RUNNER_TEMP=directory, GITHUB_ENV=str(root / "env"),
                       GITHUB_OUTPUT=str(root / "output"), app_branch="samba", tag_repo="alpine")
            return subprocess.run(["bash", "-e", "-o", "pipefail"],
                                  input=script_for("build", "Load check result"),
                                  env=env, capture_output=True, text=True)

    def test_real_check_loader_accepts_correct_success_evidence(self):
        data = dict(app_branch="samba", tag_repo="alpine", changed="true", consistent="false",
                    check_status="success", version="4.21.3")
        self.assertEqual(self.check_result(data).returncode, 0)
        data["changed"] = "false"
        self.assertEqual(self.check_result(data).returncode, 0)

    def test_real_check_loader_rejects_failed_or_wrong_target_evidence(self):
        good = dict(app_branch="samba", tag_repo="alpine", changed="true", consistent="false",
                    check_status="success", version="4.21.3")
        bad_values = [("app_branch", "aria2"), ("tag_repo", "latest"), ("changed", "null"),
                      ("consistent", "null"), ("check_status", "failure"), ("check_status", "cancelled"),
                      ("version", ""), ("version", "null"), ("version", "bad\nvalue")]
        for key, value in bad_values:
            with self.subTest(key=key, value=value):
                self.assertNotEqual(self.check_result(dict(good, **{key: value})).returncode, 0)
        self.assertNotEqual(self.check_result(None).returncode, 0)

    def test_container_testing_is_strict(self):
        metadata = script_for("container-build", "(MetaData) ${{ env.app_branch }} in Container")
        self.assertIn('${PATH_self}/scripts/ci/materialize_test_hooks.py', metadata)
        self.assertNotIn('GITHUB_WORKSPACE', job_blocks(TEXT)['container-build'])
        script = script_for("container-build", "(Test) Docker image")
        self.assertNotIn("set +e", script)
        self.assertTrue(script.startswith("set -euo pipefail\n"))
        # Simulate a failing in-container probe; do not run Docker, package tools, or network calls.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test").mkdir()
            (root / "test/test.sh").write_text("exit 7\n", encoding="utf-8")
            bin_dir = root / "bin"
            bin_dir.mkdir()
            for name, source in {
                "docker": '#!/bin/sh\nif [ "$1" = exec ] && [ "$5" = sh ]; then exit 7; fi\nexit 0\n',
                "python3": '#!/bin/sh\nexit 0\n',
            }.items():
                tool = bin_dir / name
                tool.write_text(source, encoding="utf-8")
                tool.chmod(0o755)
            env = dict(os.environ, PATH=str(bin_dir) + ":" + os.environ["PATH"], PATH_app=directory,
                       PATH_self=str(ROOT), arch_branch="linux/amd64", registry_local="localhost:5000",
                       repo_dockerhub="example/test", tag_repo="latest", container_name="test", dir_container="/tmp",
                       GITHUB_OUTPUT=str(root / "output"), time_sleep="0")
            result = subprocess.run(["bash"], input=script, env=env, cwd=directory,
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((root / "output").exists(), "Failed test emitted success")

    def test_real_image_platform_gate_handles_variants_and_mismatches(self):
        source = script_for("test-images", "Build image, execute README Test, and inspect result")
        gate = source.split('phase=platform\n', 1)[1].split('python3 scripts/ci/materialize', 1)[0]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / 'bin'
            bin_dir.mkdir()
            docker = bin_dir / 'docker'
            docker.write_text('#!/bin/sh\ncat "$FIXTURE"\n', encoding='utf-8')
            docker.chmod(0o755)
            fixture = root / 'fixture.json'
            cases = [('linux/amd64', 'linux', 'amd64', '', True),
                     ('linux/arm64', 'linux', 'arm64', 'v8', True),
                     ('linux/386', 'linux', '386', '', True),
                     ('linux/arm/v7', 'linux', 'arm', 'v7', True),
                     ('linux/arm/v7', 'linux', 'arm', 'v6', False),
                     ('linux/arm64', 'linux', 'amd64', '', False),
                     ('linux/amd64', 'windows', 'amd64', '', False)]
            for platform, os_name, arch, variant, accepted in cases:
                with self.subTest(platform=platform, actual=(os_name, arch, variant)):
                    fixture.write_text(json.dumps([dict(Os=os_name, Architecture=arch, Variant=variant)]))
                    env = dict(os.environ, PATH=str(bin_dir) + ':' + os.environ['PATH'],
                               FIXTURE=str(fixture), TARGET_PLATFORM=platform, evidence=directory, image_ref='test')
                    result = subprocess.run(['bash', '-e', '-u', '-o', 'pipefail'], input=gate,
                                            env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, accepted, result.stderr)

    def test_manual_artifact_tool_supports_download_and_pull(self):
        manual = (ROOT / ".github/workflows/download_artifact.yml").read_text(encoding="utf-8")
        self.assertIn("operation:", manual)
        self.assertIn("  download:", manual)
        self.assertIn("  pull-image:", manual)
        self.assertIn("docker image save --platform", manual)
        self.assertIn("verify_image_archive.py", manual)
        self.assertNotIn("docker push ", manual)
        self.assertNotIn("gh release ", manual)

    def test_single_target_build_and_dev_replace_retired_smoke_jobs(self):
        jobs = job_blocks(TEXT)
        self.assertNotIn("registry-smoke", TEXT)
        self.assertNotIn("registry-smoke", jobs)
        self.assertNotIn("smoke", jobs)
        self.assertNotIn("        - smoke\n", TEXT)
        self.assertNotIn("smoke-target", TEXT)
        self.assertIn("registry_local: localhost:5000", jobs["build"])
        self.assertIn("Build and push to local registry", jobs["build"])
        self.assertIn("docker pull --platform $platform", jobs["build"])
        self.assertIn("scripts/ci/build-image.sh", jobs["build"])
        self.assertIn("materialize_test_hooks.py", jobs["build"])
        dev = script_for('dev-build', 'Build, test, compare and archive locally')
        self.assertIn('compare_image_snapshot.py', dev)
        self.assertIn('UNKNOWN', dev)
        self.assertIn('Upload inspect metadata', jobs['dev-inspect'])

    def test_staging_publication_is_hard_disabled(self):
        jobs = job_blocks(TEXT)
        self.assertIn("publish: 'false'", jobs["build"])
        for job, names in {
            "build": ["(Publish) Log in to Docker Hub", "(Push) Image to ${{ env.registry_push }}", "(Upload) to Release"],
            "container-build": ["(Log in) to Docker Hub", "(Push) Image to ${{ env.registry_push }}", "(Upload) to Release"],
            "dev-build": ["Promote archived images"],
        }.items():
            for name in names:
                step = jobs[job].split("    - name: " + name + "\n", 1)[1].split("    - name:", 1)[0]
                self.assertIn("if: ${{ false }}", step, job + ': ' + name)
        dev = script_for("dev-build", "Build, test, compare and archive locally")
        self.assertNotRegex(dev, r"\bgh\s+release\b|\bdocker\s+(?:login|push)\b")
        self.assertIn('verify_image_archive.py', dev)
        self.assertIn('Upload Dev acceptance evidence', jobs['dev-build'])
        self.assertIn('Enforce complete Container acceptance', jobs['container-build'])
        self.assertIn("  schedule:", TEXT)
        self.assertIn("cron: '0 1 * * *'", TEXT)
        self.assertNotIn("  repository_dispatch:", TEXT)


if __name__ == "__main__":
    unittest.main()
