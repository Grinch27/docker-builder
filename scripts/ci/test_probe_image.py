#!/usr/bin/env python3
"""Mock-command parity tests for the standalone POSIX image version probe."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "scripts" / "ci" / "probe-image.sh"
SAMPLES = {
    "aria2": ("aria2c", "aria2 version 1.37.0\nCopyright...\n", "1.37.0"),
    "curl": ("curl", "curl 8.12.0 (x86_64-alpine-linux)\n", "8.12.0"),
    "privoxy": ("privoxy", "Privoxy version 3.0.34 (stable)\n", "3.0.34"),
    "squid": ("squid", "Squid Cache: Version 7.6\nBuilt...\n", "7.6"),
    "dnscrypt-proxy": ("dnscrypt-proxy", "2.1.18\n", "2.1.18"),
}

class ProbeImageTests(unittest.TestCase):
    def run_mock(self, app, command, output):
        with tempfile.TemporaryDirectory() as folder:
            executable = Path(folder) / command
            executable.write_text("#!/bin/sh\nprintf %s " + __import__("shlex").quote(output) + "\n")
            executable.chmod(0o755)
            env = dict(os.environ, PATH=folder + os.pathsep + os.environ.get("PATH", ""))
            return subprocess.run(["sh", str(PROBE), app], text=True,
                                  capture_output=True, env=env, check=False)

    def test_five_version_parsers(self):
        for app, (command, sample, expected) in SAMPLES.items():
            with self.subTest(app=app):
                result = self.run_mock(app, command, sample)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "version=" + expected + "\n")

    def test_empty_version_rejected(self):
        result = self.run_mock("curl", "curl", "")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Empty actual image version", result.stderr)

    def test_unknown_app_rejected(self):
        result = subprocess.run(["sh", str(PROBE), "unlisted-app"],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unsupported shared image probe", result.stderr)

    def test_bash_not_required(self):
        content = PROBE.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("#!/bin/sh\n"))
        self.assertNotIn("#!/bin/bash", content)

if __name__ == "__main__":
    unittest.main(verbosity=2)
