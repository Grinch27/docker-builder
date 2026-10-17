#!/usr/bin/env python3
# Requirements: preserve Dev/smoke comparison decisions and JSON schema after extracting the shared CLI.
# Unknowns/research: registry visibility is represented by saved evidence, not live network requests.
# Optimization: small JSON fixtures need no Docker, package installation or external services.
# Risks/verification: platform/version/config differences, unknown evidence, missing data and malformed JSON.
"""Exercise the actual saved-evidence comparison command from an unrelated directory."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("compare_image_snapshot.py")
PLATFORM = "linux/amd64"


class ImageSnapshotComparisonTests(unittest.TestCase):
    def setUp(self):
        self.image = {"Os": "linux", "Architecture": "amd64", "Config": {
            "Env": ["A=1"], "Labels": {"version": "1.0"}, "Cmd": ["/start"]}}
        self.candidate = {"actual_version": "1.0", "source": {"image_inspect": [self.image]}}
        self.baseline = {"registries": {name: {
            "status": "present", "source": {"platforms": {PLATFORM: {
                "status": "present", "image": copy.deepcopy(self.image)}}}}
            for name in ("dockerhub", "ghcr")}}

    def compare(self, mode="auto"):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, candidate, output = [root / name for name in ("baseline", "candidate", "output")]
            for path, value in [(baseline, self.baseline), (candidate, self.candidate)]:
                path.write_text(json.dumps(value), encoding="utf-8")
            before = [baseline.read_bytes(), candidate.read_bytes()]
            result = subprocess.run([sys.executable, str(SCRIPT), str(baseline), str(candidate),
                                     PLATFORM, mode, str(output)], cwd=directory,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(before, [baseline.read_bytes(), candidate.read_bytes()])
            return json.loads(output.read_text(encoding="utf-8"))

    def test_same_evidence_and_docker_oci_key_casing(self):
        remote = self.baseline["registries"]["ghcr"]["source"]["platforms"][PLATFORM]["image"]
        remote["config"] = remote.pop("Config")
        remote["os"] = remote.pop("Os")
        remote["architecture"] = remote.pop("Architecture")
        result = self.compare()
        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["comparison"], {"result": "SAME", "candidate_changed": False})
        self.assertTrue(all(r["result"] == "SAME" and not r["promotion_required"]
                            for r in result["registries"].values()))

    def test_real_changes_require_both_registry_updates(self):
        for field, value, reason in [("Architecture", "arm64", "platform"),
                                     ("Variant", "v8", "platform"),
                                     ("Config", {"Env": ["A=2"]}, "runtime_config_or_labels")]:
            with self.subTest(field=field):
                original = copy.deepcopy(self.image)
                self.image[field] = value
                result = self.compare()
                self.assertEqual(result["comparison"], {"result": "CHANGED", "candidate_changed": True})
                self.assertIn(reason, result["registries"]["dockerhub"]["reasons"])
                self.assertTrue(all(r["promotion_required"] for r in result["registries"].values()))
                self.image.clear()
                self.image.update(original)
        self.candidate["actual_version"] = "2.0"
        result = self.compare()
        self.assertIn("actual_version", result["registries"]["dockerhub"]["reasons"])
        self.assertEqual(result["comparison"]["result"], "CHANGED")

    def test_missing_and_unobservable_evidence_depends_on_explicit_build(self):
        self.baseline["registries"] = {"dockerhub": {"status": "missing"},
                                       "ghcr": {"status": "unobservable"}}
        self.assertEqual(self.compare()["comparison"]["result"], "UNKNOWN")
        result = self.compare("build")
        self.assertEqual(result["comparison"]["result"], "REPAIR")
        self.assertTrue(result["registries"]["dockerhub"]["promotion_required"])
        self.assertFalse(result["registries"]["ghcr"]["promotion_required"])

    def test_unknown_evidence_cannot_be_counted_as_unchanged_or_success(self):
        self.baseline["registries"]["ghcr"] = {"status": "inspect_failed"}
        self.candidate["actual_version"] = "2.0"
        result = self.compare()
        self.assertEqual(result["comparison"], {"result": "UNKNOWN", "candidate_changed": True})
        self.assertIn("registry_status=inspect_failed", result["registries"]["ghcr"]["reasons"])

    def test_missing_platform_stays_missing(self):
        self.baseline["registries"]["dockerhub"]["source"]["platforms"] = {}
        result = self.compare()
        self.assertEqual(result["registries"]["dockerhub"]["result"], "MISSING")
        self.assertTrue(result["registries"]["dockerhub"]["promotion_required"])

    def test_missing_published_version_requires_evidence_or_remains_unknown(self):
        self.image["Config"]["Labels"] = {}
        for registry in self.baseline["registries"].values():
            registry["source"]["platforms"][PLATFORM]["image"]["Config"]["Labels"] = {}
        result = self.compare()
        self.assertEqual(result["comparison"]["result"], "UNKNOWN")
        self.assertIn("published_actual_version_missing", result["registries"]["dockerhub"]["reasons"])
        for registry in self.baseline["registries"].values():
            registry["source"]["parsed"] = {"nested": [{"org.opencontainers.image.version": "1.0"}]}
        self.assertEqual(self.compare()["comparison"]["result"], "SAME")

    def test_malformed_json_fails_without_emitting_a_success_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline, candidate, output = [root / name for name in ("baseline", "candidate", "output")]
            baseline.write_text("{invalid", encoding="utf-8")
            candidate.write_text(json.dumps(self.candidate), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(baseline), str(candidate),
                                     PLATFORM, "build", str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
