#!/usr/bin/env python3
# Requirements: only a configured Tag's exact independent Dockerfile can be selected.
# Unknowns/research: Docker execution is verified separately through nonpublishing CI.
# Optimization: filesystem fixtures exercise resolution before the repository migration.
# Risks/verification: absent versus empty Tags, traversal, symlinks and forbidden shared fallbacks.
"""Strict Tag-to-file resolution without requiring the repository layout to migrate first."""
import os
import subprocess
import tempfile
from pathlib import Path
import unittest

import catalog


class TagLayoutTests(unittest.TestCase):
    def test_default_is_only_for_absent_tag(self):
        self.assertEqual(catalog.target_tag({}), 'latest')
        self.assertEqual(catalog.dockerfile_name('runner'), 'latest.Dockerfile')
        for value in ['', None, 0, False, '../dev', 'a/b', '..', 'x..y', 'x\\y', 'a\n']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                catalog.target_tag({'tag': value})

    def test_explicit_tags_remain_exact_and_application_names_are_safe(self):
        for tag in ['dev', 'main', 'nightly', 'actions-slim', 'A_1.0']:
            self.assertEqual(catalog.dockerfile_name('runner', tag), tag + '.Dockerfile')
        for app in ['', '../runner', '..', '/runner', 'runner/x']:
            with self.subTest(app=app), self.assertRaises(ValueError):
                catalog.dockerfile_name(app, 'latest')

    def test_missing_file_never_falls_back_and_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            app = root / 'application/runner'
            app.mkdir(parents=True)
            for filename in ['Dockerfile', 'latest.Dockerfile', 'dev.Dockerfile']:
                (app / filename).write_text('FROM scratch\n')
            with self.assertRaisesRegex(ValueError, 'runner:actions:.*actions.Dockerfile'):
                catalog.resolve_dockerfile(root, 'runner', 'actions')
            (app / 'actions.Dockerfile').symlink_to('dev.Dockerfile')
            with self.assertRaises(ValueError):
                catalog.resolve_dockerfile(root, 'runner', 'actions')
            (app / 'actions.Dockerfile').unlink()
            (app / 'actions.Dockerfile').write_text('FROM scratch\n')
            self.assertEqual(catalog.resolve_dockerfile(root, 'runner', 'actions'), app / 'actions.Dockerfile')

    def test_get_defaults_only_to_a_registered_latest_target(self):
        config = {'apps': {'runner': {'repository': 'example/runner', 'platforms': ['linux/amd64'],
                                      'base_image': 'scratch', 'targets': [{'tag': 'dev'}]}}}
        with self.assertRaisesRegex(ValueError, 'Unknown target'):
            catalog.get(config, 'runner')
        config['apps']['runner']['targets'] = [{}]
        self.assertEqual(catalog.get(config, 'runner')['dockerfile'], 'latest.Dockerfile')

    def test_builder_fails_before_docker_for_missing_case_mismatch_and_override(self):
        builder = Path(__file__).resolve().parents[2] / 'scripts/ci/build-image.sh'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'bin').mkdir()
            docker = root / 'bin/docker'
            docker.write_text('#!/bin/sh\ntouch "$DOCKER_CALLED"\n')
            docker.chmod(0o755)
            called = root / 'called'
            env = dict(os.environ, PATH=str(root / 'bin') + ':' + os.environ['PATH'],
                       DOCKER_CALLED=str(called), registry_local='127.0.0.1:5000', repo_dockerhub='example/test',
                       tag_repo='actions', version='1.0',
                       arch_branch='linux/amd64', base_image='scratch', build_tag='actions')
            for name in ['Dockerfile', 'latest.Dockerfile', 'dev.Dockerfile', 'Actions.Dockerfile']:
                (root / name).write_text('FROM scratch\n')
            result = subprocess.run(['bash', str(builder)], cwd=root, env=env, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(called.exists())
            (root / 'actions.Dockerfile').write_text('FROM scratch\n')
            bad = dict(env, dockerfile='dev.Dockerfile')
            result = subprocess.run(['bash', str(builder)], cwd=root, env=bad, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(called.exists())
            subprocess.run(['bash', str(builder)], cwd=root, env=env, check=True, capture_output=True)
            self.assertTrue(called.exists())


if __name__ == '__main__':
    unittest.main()
