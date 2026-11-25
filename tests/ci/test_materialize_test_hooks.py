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


    def test_adguardvpn_meta_uses_configured_channel_and_rejects_failed_probes(self):
        tag_list = ('[{"name":"v1.9.3-nightly.1"},{"name":"v1.2-release"},'
                    '{"name":"v1.8.1-rc.2-beta"},{"name":"v1.1-release"}]')
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_temp(directory)
            hooks.materialize(root, 'adguardvpn-cli', 'meta')
            probe = root / 'application/adguardvpn-cli/meta-app/meta-app.sh'
            bindir = root / 'bin'
            bindir.mkdir()
            commands = {
                'apk': 'exit 0\n',
                'curl': 'printf "%s" "$ADGUARD_TAGS_FIXTURE"\nexit "$ADGUARD_CURL_STATUS"\n',
            }
            for name, body in commands.items():
                command = bindir / name
                command.write_text('#!/bin/sh\n' + body, encoding='utf-8')
                command.chmod(0o755)

            def run_probe(build_arg, tags=tag_list, curl_status=0):
                env = {
                    'PATH': str(bindir) + os.pathsep + os.environ.get('PATH', os.defpath),
                    'ADGUARD_TAGS_FIXTURE': tags,
                    'ADGUARD_CURL_STATUS': str(curl_status),
                }
                if build_arg is not None:
                    env['build_arg'] = build_arg
                return subprocess.run(['/bin/sh', str(probe)], cwd=root, env=env,
                                      capture_output=True, text=True)

            for channel, expected in [('release', '1.2'), ('beta', '1.8.1-rc.2'),
                                      ('nightly', '1.9.3-nightly.1')]:
                with self.subTest(channel=channel):
                    result = run_probe('update_channel=' + channel)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, 'version=' + expected + '\n')

            release = 'update_channel=release'
            failures = [
                ('missing argument', None, tag_list, 0),
                ('invalid channel', 'update_channel=latest', tag_list, 0),
                ('duplicate channel', release + ',update_channel=nightly', tag_list, 0),
                ('HTTP failure with response body', release, tag_list, 22),
                ('malformed JSON after a valid match', release, tag_list + '\n[', 0),
                ('non-array JSON', release, '{"first":{"name":"v1.2-release"}}', 0),
                ('no match', release, '[{"name":"v9.9-nightly"}]', 0),
                ('empty version', release, '[{"name":"v-release"}]', 0),
                ('prerelease used as release', release, '[{"name":"v1.8.1-rc.2-release"}]', 0),
            ]
            for name, build_arg, tags, curl_status in failures:
                with self.subTest(failure=name):
                    result = run_probe(build_arg, tags, curl_status)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn('version=', result.stdout)

    def test_canonical_version_parsers_with_command_fixtures(self):
        # The retired shared probe was an oracle only. Test the maintained README scripts.
        samples = {'aria2': ('aria2c', 'aria2 version 1.37.0\nCopyright...\n', '1.37.0'), 'curl': ('curl', 'curl 8.12.0 (x86_64-alpine-linux)\n', '8.12.0'), 'privoxy': ('privoxy', 'Privoxy version 3.0.34 (stable)\n', '3.0.34'), 'squid': ('squid', 'Squid Cache: Version 7.6\nBuilt...\n', '7.6'), 'dnscrypt-proxy': ('dnscrypt-proxy', '2.1.18\n', '2.1.18')}
        samples['doh-nosni'] = samples['dnscrypt-proxy']
        samples['adguardvpn-cli'] = ('adguardvpn-cli',
                                    'Created data directory /root/.local/share/adguardvpn-cli\n'
                                    'AdGuard VPN CLI v1.7.12\n', '1.7.12')
        for app, (command, output, expected) in samples.items():
            with self.subTest(app=app), tempfile.TemporaryDirectory() as directory:
                root = self.make_temp(directory)
                hooks.materialize(root, app)
                bindir = root / 'bin'
                bindir.mkdir()
                executable = bindir / command
                env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get('PATH', ''))
                cases = [(output, expected), ('', None), ('bad\x01version\n', None)]
                if app == 'adguardvpn-cli':
                    cases.extend([
                        ('AdGuard VPN CLI v1.8.1-rc.2\n', '1.8.1-rc.2'),
                        ('AdGuard VPN CLI v1.9.3-nightly.1\n', '1.9.3-nightly.1'),
                        ('AdGuard VPN CLI v1.9.3-nightly.1\nAdGuard VPN CLI v1.8.1-rc.2\n', None),
                    ])
                for sample, version in cases:
                    executable.write_text('#!/bin/sh\nprintf %s ' + __import__('shlex').quote(sample) + '\n')
                    executable.chmod(0o755)
                    result = subprocess.run(['sh', str(root/'application'/app/'test/test.sh')],
                                            env=env, capture_output=True, text=True)
                    self.assertEqual(result.returncode == 0, version is not None, (app, repr(sample), result.stderr))
                    if version is not None:
                        self.assertEqual(result.stdout, 'version=' + version + '\n')

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


    def test_direct_version_scripts_have_posix_shell_syntax(self):
        cases = [('curl', 'meta'), ('doh-nosni', 'meta'), ('novnc_alpine', 'meta'),
                 ('novnc', 'test'), ('baidunetdisk', 'test')]
        for app, kind in cases:
            with self.subTest(app=app, kind=kind):
                source = hooks.scripts(ROOT, kind)[app]
                result = subprocess.run(['sh', '-n'], input=source,
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_direct_installed_version_fixtures(self):
        import json
        test_sources = hooks.scripts(ROOT)
        meta = hooks.scripts(ROOT, 'meta')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bindir = root / 'bin'
            bindir.mkdir()
            for name in ('apk', 'apt-get'):
                cmd = bindir / name
                cmd.write_text('#!/bin/sh\nexit 0\n')
                cmd.chmod(0o755)
            env = dict(os.environ, PATH=str(bindir) + os.pathsep + os.environ.get('PATH', ''))
            for app, command, output, expected in [
                ('curl', 'curl', 'curl 8.12.0 (Alpine)\n', '8.12.0'),
                ('doh-nosni', 'dnscrypt-proxy', '2.1.18\n', '2.1.18'),
            ]:
                with self.subTest(app=app):
                    cmd = bindir / command
                    cmd.write_text('#!/bin/sh\nprintf %s ' +
                                   __import__('shlex').quote(output) + '\n')
                    cmd.chmod(0o755)
                    result = subprocess.run(['sh', '-c', meta[app]], capture_output=True,
                                            text=True, env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, 'version=' + expected + '\n')
            apk_db = root / 'installed'
            apk_db.write_text('P:other\nV:0.1\n\nP:novnc\nV:1.6.0-r0\n\n')
            script = meta['novnc_alpine'].replace('/lib/apk/db/installed', str(apk_db))
            result = subprocess.run(['sh', '-c', script], capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'version=1.6.0-r0\n')
            apk_db.write_text('P:other\nV:0.1\n\n')
            self.assertNotEqual(subprocess.run(['sh', '-c', script], env=env,
                                               capture_output=True).returncode, 0)
            manifest = root / 'package.json'
            script = test_sources['novnc'].replace('/opt/bin/noVNC/package.json', str(manifest))
            manifest.write_text(json.dumps({'name': '@novnc/novnc', 'version': '1.7.0'}, indent=2))
            result = subprocess.run(['sh', '-c', script], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'version=1.7.0\n')
            manifest.write_text('{"name":"@novnc/novnc"}')
            self.assertNotEqual(subprocess.run(['sh', '-c', script],
                                               capture_output=True).returncode, 0)
            cmd = bindir / 'dpkg-query'
            cmd.write_text('#!/bin/sh\nprintf "4.17.7\n"\n')
            cmd.chmod(0o755)
            result = subprocess.run(['sh', '-c', test_sources['baidunetdisk']],
                                    capture_output=True, text=True, env=env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'version=4.17.7\n')
            cmd.write_text('#!/bin/sh\nexit 4\n')
            self.assertNotEqual(subprocess.run(['sh', '-c', test_sources['baidunetdisk']],
                                               env=env, capture_output=True).returncode, 0)

if __name__=='__main__':
    unittest.main(verbosity=2)
