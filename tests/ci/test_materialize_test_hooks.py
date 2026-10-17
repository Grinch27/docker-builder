#!/usr/bin/env python3
# Requirements: retain CI behavior coverage independently of runtime script location.
# Unknowns/research: external execution is covered by nonpublishing Actions acceptance.
# Optimization: keep fixtures in tests/ci and business code in scripts/ci.
# Risks/verification: explicit import and script paths; no reduced failure boundaries.
"""README HTML-table script extraction, equality and materialization tests."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'/'ci'))
import catalog
import materialize_test_hooks as hooks

class EmbeddedTests(unittest.TestCase):
    def make_temp(self,directory):
        root=Path(directory)
        shutil.copyfile(ROOT/'README.md',root/'README.md')
        return root

    def test_table_contains_all_24_scripts(self):
        source=hooks.scripts(ROOT)
        self.assertEqual(len(source),24)
        self.assertEqual(set(source),set(catalog.catalog_from_readme(ROOT/'README.md')['apps']))
        self.assertIn('/etc/openwrt_release',source['openwrt'])
        self.assertIn('Runner.Listener',source['runner'])
        self.assertIn('import torch',source['sdnext-dev'])

    def test_existing_18_are_byte_identical(self):
        sources=hooks.scripts(ROOT)
        count=0
        for app,script in sources.items():
            path=ROOT/'application'/app/'test'/'test.sh'
            if path.is_file():
                self.assertEqual(path.read_bytes(),script.encode('utf-8'),app)
                count+=1
        self.assertLessEqual(count,18)

    def test_24_materialize_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.make_temp(d)
            for name,script in hooks.scripts(root).items():
                self.assertEqual(hooks.materialize(root,name),'generated')
                self.assertEqual(hooks.materialize(root,name),'existing')
                self.assertEqual((root/'application'/name/'test'/'test.sh').read_bytes(),
                                 script.encode('utf-8'))

    def test_refuse_to_overwrite_foreign_script(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.make_temp(d)
            target=root/'application'/'openwrt'/'test'/'test.sh'
            target.parent.mkdir(parents=True)
            target.write_text('#!/bin/sh\necho changed\n')
            with self.assertRaisesRegex(ValueError,'differs'):
                hooks.materialize(root,'openwrt')

    def test_reject_symlinked_script_ancestors(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.make_temp(d)
            outside=root/'outside'
            outside.mkdir()
            app_dir=root/'application'/'aria2'
            app_dir.mkdir(parents=True)
            for kind, subdir in (('test','test'), ('meta','meta-app')):
                generated_dir=app_dir/subdir
                generated_dir.symlink_to(outside,target_is_directory=True)
                with self.assertRaisesRegex(ValueError,'Symlink in generated script path'):
                    hooks.materialize(root,'aria2',kind)
                self.assertEqual(list(outside.iterdir()),[])
                generated_dir.unlink()
            app_dir.rmdir()
            app_dir.symlink_to(outside,target_is_directory=True)
            with self.assertRaisesRegex(ValueError,'Symlink in generated script path'):
                hooks.materialize(root,'aria2')
            self.assertEqual(list(outside.iterdir()),[])

    def test_reject_bad_markers_and_unknown_app(self):
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Malformed'):
            catalog.embedded_tests_from_text(text.replace(
                '<!-- app-test:runner:start -->','<!-- missing -->',1))
        with self.assertRaisesRegex(ValueError,'No embedded'):
            hooks.materialize(ROOT,'not-an-app')

    def test_aria2_shell_command_matches_original_oracle(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.make_temp(d)
            hooks.materialize(root,'aria2')
            bin_dir=root/'bin'
            bin_dir.mkdir()
            cmd=bin_dir/'aria2c'
            cmd.write_text('#!/bin/sh\nprintf "aria2 version 1.37.0\\n"\n')
            cmd.chmod(0o755)
            env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ.get('PATH',''))
            result=subprocess.run(['sh',str(root/'application'/'aria2'/'test'/'test.sh')],
                                  capture_output=True,text=True,check=True,env=env)
            self.assertEqual(result.stdout,'version=1.37.0\n')


    def test_meta_23_scripts_and_missing_ffmpeg(self):
        meta=hooks.scripts(ROOT,'meta')
        self.assertEqual(len(meta),23)
        self.assertNotIn('ffmpeg',meta)
        self.assertEqual(set(meta)|{'ffmpeg'},set(hooks.scripts(ROOT)))
        with tempfile.TemporaryDirectory() as d:
            root=self.make_temp(d)
            for name,script in meta.items():
                self.assertEqual(hooks.materialize(root,name,'meta'),'generated')
                self.assertEqual(hooks.materialize(root,name,'meta'),'existing')
                self.assertEqual((root/'application'/name/'meta-app'/'meta-app.sh').read_bytes(),
                                 script.encode('utf-8'))
            self.assertEqual(hooks.materialize(root,'ffmpeg','meta'),'missing')
            self.assertFalse((root/'application'/'ffmpeg'/'meta-app'/'meta-app.sh').exists())

    def test_meta_refuses_foreign_script_and_markers(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.make_temp(d)
            target=root/'application'/'aria2'/'meta-app'/'meta-app.sh'
            target.parent.mkdir(parents=True)
            target.write_text('#!/bin/sh\necho changed\n')
            with self.assertRaisesRegex(ValueError,'differs'):
                hooks.materialize(root,'aria2','meta')
            target.unlink()
            target.symlink_to(root/'README.md')
            with self.assertRaisesRegex(ValueError,'Symlink'):
                hooks.materialize(root,'aria2','meta')
        source=(ROOT/'README.md').read_text(encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Malformed'):
            catalog.embedded_meta_from_text(source.replace(
                '<!-- app-meta:runner:start -->','<!-- broken -->',1))
        with self.assertRaisesRegex(ValueError,'No embedded'):
            hooks.materialize(ROOT,'unknown-app','meta')


    def test_canonical_version_parsers_with_command_fixtures(self):
        # The retired shared probe was an oracle only. Test the maintained README scripts.
        samples = {'aria2': ('aria2c', 'aria2 version 1.37.0\nCopyright...\n', '1.37.0'), 'curl': ('curl', 'curl 8.12.0 (x86_64-alpine-linux)\n', '8.12.0'), 'privoxy': ('privoxy', 'Privoxy version 3.0.34 (stable)\n', '3.0.34'), 'squid': ('squid', 'Squid Cache: Version 7.6\nBuilt...\n', '7.6'), 'dnscrypt-proxy': ('dnscrypt-proxy', '2.1.18\n', '2.1.18')}
        samples['doh-nosni'] = samples['dnscrypt-proxy']
        for app, (command, output, expected) in samples.items():
            with self.subTest(app=app), tempfile.TemporaryDirectory() as directory:
                root = self.make_temp(directory)
                hooks.materialize(root, app)
                bindir = root / 'bin'
                bindir.mkdir()
                executable = bindir / command
                env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get('PATH', ''))
                for sample, accepted in [(output, True), ('', False), ('bad\x01version\n', False)]:
                    executable.write_text('#!/bin/sh\nprintf %s ' + __import__('shlex').quote(sample) + '\n')
                    executable.chmod(0o755)
                    result = subprocess.run(['sh', str(root/'application'/app/'test/test.sh')],
                                            env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, accepted, (app, repr(sample), result.stderr))
                    if accepted:
                        self.assertEqual(result.stdout, 'version=' + expected + '\n')

    def test_canonical_dns_version_uses_first_line(self):
        # README semantics deliberately accept a first-line version followed by a banner.
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_temp(directory)
            hooks.materialize(root, 'dnscrypt-proxy')
            bindir = root / 'bin'
            bindir.mkdir()
            executable = bindir / 'dnscrypt-proxy'
            executable.write_text('#!/bin/sh\nprintf "2.1.18\\nextra banner\\n"\n')
            executable.chmod(0o755)
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get('PATH', ''))
            result = subprocess.run(['sh', str(root/'application/dnscrypt-proxy/test/test.sh')],
                                    env=env, capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout, 'version=2.1.18\n')

if __name__=='__main__':
    unittest.main(verbosity=2)
