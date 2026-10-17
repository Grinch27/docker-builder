#!/usr/bin/env python3
# Requirements: fail closed on failed check evidence and prohibit publication during acceptance.
# Unknowns/research: GitHub-hosted execution and registry publication remain unverified locally.
# Risks/verification: execute real check-result shell with fixtures; check all inline Bash syntax.
# Optimization: use standard-library extraction; actionlint validates the full YAML separately.
"""Verify failure boundaries and executable shell in the single core workflow."""

import importlib.util
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
spec = importlib.util.spec_from_file_location("workflow_graph", ROOT / "scripts/ci/gpt_workflow_graph.py")
graph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graph)


def script_for(job, name):
    block = graph.job_blocks(TEXT)[job]
    step = block.split("    - name: " + name + "\n", 1)[1].split("    - name:", 1)[0]
    match = re.search(r"^      run: \|[-+]?\n((?:        [^\n]*\n|\n)*)", step, re.MULTILINE)
    if not match:
        raise ValueError("Missing literal shell for " + name)
    return textwrap.dedent(match[1])


class WorkflowContractTests(unittest.TestCase):
    def test_job_graph_has_no_dangling_or_nested_calls(self):
        graph.validate(ROOT)

    def test_all_inline_shell_parses(self):
        scripts = re.findall(r"^      run: \|[-+]?\n((?:        [^\n]*\n|\n)*)", TEXT, re.MULTILINE)
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

    def test_staging_publication_is_hard_disabled(self):
        jobs = graph.job_blocks(TEXT)
        self.assertIn("WORKFLOW_READ_ONLY: 'true'", jobs["plan"])
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
        self.assertNotIn("  schedule:", TEXT)
        self.assertNotIn("  repository_dispatch:", TEXT)


if __name__ == "__main__":
    unittest.main()
