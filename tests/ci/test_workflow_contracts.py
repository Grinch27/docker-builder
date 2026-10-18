#!/usr/bin/env python3
# Requirements: one input, one Container builder, shared diagnostics and strict evidence gates.
# Unknowns/research: GitHub-hosted execution and registry publication remain unverified locally.
# Risks/verification: exercise probe statuses, exact actual/label versions and platform/Test/diagnostic failure gates.
# Optimization: one standard-library graph/contract gate; actionlint validates YAML separately.
"""Verify failure boundaries and executable shell in the single core workflow."""

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import shlex
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
    required = {"runner-image", "plan", "fetch-versions", "monitor",
                "diagnostic-layers", "diagnostic-platforms", "diagnostic-collect",
                "diagnostic-validate", "container-build"}
    assert required == blocks.keys(), "Core Job set changed"
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
    def test_graph_and_planning_validation(self):
        validate_workflow(ROOT)
        for source in [TEXT.replace('python3 -m unittest discover','echo skipped tests'),
                       TEXT.replace('  plan:\n','  plan:\n    continue-on-error: true\n',1),
                       TEXT.replace('needs.plan.outputs.build','needs.plan.outputs.retired')]:
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                flow=root/'.github/workflows'
                flow.mkdir(parents=True)
                (flow/'gpt_dev.yml').write_text(source)
                (flow/'download_artifact.yml').write_text('jobs:\n  pull-image:\n')
                with self.assertRaises(AssertionError):
                    validate_workflow(root)

    def test_manual_tool_reusable_references_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            flow=root/'.github/workflows'
            flow.mkdir(parents=True)
            (flow/'gpt_dev.yml').write_text(TEXT)
            (flow/'download_artifact.yml').write_text('jobs:\n  pull-image:\n    uses: ./.github/workflows/retired.yml\n')
            with self.assertRaisesRegex(AssertionError,'Dangling reusable'):
                validate_workflow(root)

    def test_only_targets_is_public_and_other_builders_are_absent(self):
        inputs=TEXT.split('  workflow_dispatch:\n    inputs:\n',1)[1].split('\npermissions:',1)[0]
        self.assertEqual(set(re.findall(r'^      ([a-z_]+):',inputs,re.MULTILINE)),{'targets'})
        self.assertIn('default: vlmcsd',inputs)
        for old in ['execution_route','GPT_STAGING','custom_env','force_push','publish:','may_publish:',
                    'needs.plan.outputs.verify','env-indocker','--load','free_disk_before_compress']:
            self.assertNotIn(old,TEXT)
        for name in ['container-build','diagnostic-layers','diagnostic-platforms','diagnostic-collect','diagnostic-validate']:
            self.assertIn("needs.plan.outputs.build == 'true'",job_blocks(TEXT)[name])
        for name in ['fetch-versions','monitor']:
            self.assertIn("needs.plan.outputs.monitor == 'true'",job_blocks(TEXT)[name])

    def test_no_external_write_implementation_or_legacy_marker_parser(self):
        self.assertNotRegex(TEXT,r'\b(?:docker\s+(?:login|push)|gh\s+release|git\s+push)\b')
        self.assertNotRegex(TEXT,r'--dest-creds|release-action|secrets\.')
        planner=(ROOT/'scripts/ci/workflow_plan.py').read_text()
        self.assertNotIn('head_commit',planner)
        self.assertNotIn('GITHUB_EVENT_PATH',planner)
        self.assertIn('127.0.0.1:5000',TEXT)
        self.assertIn("cron: '0 1 * * *'",TEXT)

    def test_daemon_is_host_socket_only_and_storage_is_observed(self):
        block=job_blocks(TEXT)['container-build']
        self.assertIn('/var/run/docker.sock:/var/run/docker.sock',block)
        self.assertIn('DOCKER_HOST: unix:///var/run/docker.sock',block)
        for old in ['dockerd --host','service docker','daemon.json','--pid=host','gcc_install']:
            self.assertNotIn(old,block)
        self.assertIn('docker-ce-cli docker-buildx-plugin',block)
        self.assertIn('.DockerRootDir',block)
        self.assertIn('src=$root,dst=/data,readonly',block)
        self.assertIn('needs.runner-image.outputs.CONTAINER_IMAGE',block)

    def test_all_inline_shell_parses(self):
        scripts=re.findall(r'^      run: (?:&[\w-]+ )?\|[-+]?\n((?:        [^\n]*\n|\n)*)',TEXT,re.MULTILINE)
        self.assertGreater(len(scripts),15)
        for index,source in enumerate(scripts):
            source=re.sub(r'\$\{\{.*?\}\}','CONTEXT',textwrap.dedent(source))
            with self.subTest(script=index):
                result=subprocess.run(['bash','-n'],input=source,text=True,capture_output=True)
                self.assertEqual(result.returncode,0,result.stderr)

    def diagnostic_result(self,mutate=None):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            files={'diagnostics-layer-summary/base_layers.json':{'alpine:latest':['sha256:a']},
                   'diagnostics-layer-summary/aggregated_layers.json':{'Layers':['sha256:a']}}
            for arch in ['amd64','arm64']:
                files[f'layers-alpine-{arch}/layers.json']=['sha256:a']
                files[f'layer-info-alpine-{arch}/image_alpine.json']=dict(image='alpine:latest',architecture=arch,raw_data={'Layers':['sha256:a']})
            needs={k:{'result':'success'} for k in ['diagnostic-layers','diagnostic-platforms','diagnostic-collect']}
            if mutate:
                mutate(files,needs)
            for name,data in files.items():
                path=root/'diagnostic-contracts'/name
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(json.dumps(data))
            env=dict(os.environ,RUNNER_TEMP=directory,DIAGNOSTIC_IMAGES='["alpine:latest"]',JOB_RESULTS=json.dumps(needs))
            return subprocess.run(['bash','-e','-o','pipefail'],input=script_for('diagnostic-validate','Check selected diagnostic contracts'),env=env,capture_output=True,text=True)

    def test_shared_diagnostic_gate_checks_actual_contracts(self):
        result=self.diagnostic_result()
        self.assertEqual(result.returncode,0,result.stderr)
        cases=[lambda f,n:f.pop('layer-info-alpine-arm64/image_alpine.json'),
               lambda f,n:f['layer-info-alpine-arm64/image_alpine.json'].update(architecture='amd64'),
               lambda f,n:f['diagnostics-layer-summary/base_layers.json'].clear(),
               lambda f,n:f['diagnostics-layer-summary/aggregated_layers.json'].update(Layers=[])]
        for change in cases:
            self.assertNotEqual(self.diagnostic_result(change).returncode,0)
        for job in ['diagnostic-layers','diagnostic-platforms','diagnostic-collect']:
            for status in ['failure','cancelled','skipped']:
                self.assertNotEqual(self.diagnostic_result(lambda f,n:n[job].update(result=status)).returncode,0)

    def test_actual_image_platform_gate_handles_variants_and_wrong_images(self):
        source=script_for('container-build','Test, compare and export every configured platform')
        gate=source.split('  phase=platform\n',1)[1].split('  phase=test\n',1)[0]
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'image.json'
            cases=[('linux/amd64','linux','amd64','',True),('linux/arm64','linux','arm64','v8',True),
                   ('linux/386','linux','386','',True),('linux/arm/v7','linux','arm','v7',True),
                   ('linux/arm/v7','linux','arm','v6',False),('linux/arm64','linux','amd64','',False),
                   ('linux/amd64','windows','amd64','',False)]
            for platform,os_name,arch,variant,accepted in cases:
                path.write_text(json.dumps([dict(Os=os_name,Architecture=arch,Variant=variant)]))
                result=subprocess.run(['bash','-e','-u','-o','pipefail'],input=gate,text=True,capture_output=True,
                                      env=dict(os.environ,evidence=directory,platform=platform))
                self.assertEqual(result.returncode==0,accepted,result.stderr)

    def pipeline(self,root,test_exit='0',baseline='missing',platforms='linux/amd64',test_version='1.0',image_version='1.0'):
        import io
        import tarfile
        tools=root/'bin'
        tools.mkdir()
        work=root/'app/test'
        work.mkdir(parents=True)
        (work/'test.sh').write_text('echo version=1.0\n')
        for platform in platforms.split(','):
            fixture=root/(platform.replace('/','_')+'.tar')
            with tarfile.open(fixture,'w') as archive:
                for name,data in {'manifest.json':json.dumps([dict(Config='config.json',Layers=['layer.tar'])]).encode(),
                                  'config.json':json.dumps(dict(os='linux',architecture=platform.split('/')[1])).encode(),
                                  'layer.tar':b'fixture'}.items():
                    item=tarfile.TarInfo(name)
                    item.size=len(data)
                    archive.addfile(item,io.BytesIO(data))
        docker=tools/'docker'
        docker.write_text('#!'+sys.executable+'\n'+textwrap.dedent('''
            import json,os,shutil,sys
            a=sys.argv[1:]
            if a[:2]==['image','inspect']:
                assert '--platform' in a, 'Inspect must select a platform explicitly'
                platform=a[a.index('--platform')+1]
                print(json.dumps([dict(Os='linux',Architecture=platform.split('/')[1],Config={'Labels':{'version':os.environ['IMAGE_VERSION']}})]))
            elif a[:2]==['image','save']:
                platform=a[a.index('--platform')+1]
                shutil.copyfile(os.path.join(os.environ['FIXTURE_ROOT'],platform.replace('/','_')+'.tar'),a[a.index('--output')+1])
            elif a and a[0]=='exec':
                print('version='+os.environ['TEST_VERSION'])
                sys.exit(int(os.environ['TEST_EXIT']))
        '''))
        docker.chmod(0o755)
        python=tools/'python3'
        python.write_text('#!/bin/sh\ncase "$1" in *materialize_test_hooks.py) exit 0;; esac\nexec '+shlex.quote(sys.executable)+' "$@"\n')
        python.chmod(0o755)
        metadata=root/'metadata'
        metadata.mkdir()
        (metadata/'baseline.json').write_text(json.dumps({'registries':{k:{'status':baseline} for k in ['dockerhub','ghcr']}}))
        output=root/'output'
        output.mkdir()
        env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'],PATH_app=str(work.parent),PATH_self=str(ROOT),
                 PATH_output=str(output),PATH_metadata=str(metadata),arch_branch=platforms,registry_local='127.0.0.1:5000',
                 repo_dockerhub='example/image',tag_repo='latest',app_branch='fixture',version='1.0',GITHUB_SHA='fixture-sha',
                 FIXTURE_ROOT=str(root),TEST_EXIT=test_exit,TEST_VERSION=test_version,IMAGE_VERSION=image_version)
        return subprocess.run(['bash','-e','-u','-o','pipefail'],cwd=ROOT,env=env,capture_output=True,text=True,
                              input=script_for('container-build','Test, compare and export every configured platform'))

    def test_real_container_pipeline_exports_verified_success_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            result=self.pipeline(root)
            self.assertEqual(result.returncode,0,result.stderr)
            record=json.loads((root/'metadata/linux_amd64/result.json').read_text())
            self.assertEqual((record['platform'],record['phase'],record['exit_code']),('linux/amd64','complete',0))
            exports=json.loads((root/'metadata/exports.json').read_text())['archives']
            self.assertEqual(len(exports),1)
            self.assertTrue((root/'output'/exports[0]['filename']).is_file())

    def test_three_platforms_are_inspected_tested_and_exported_independently(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            platforms='linux/amd64,linux/arm64,linux/386'
            result=self.pipeline(root,platforms=platforms)
            self.assertEqual(result.returncode,0,result.stderr)
            exports=json.loads((root/'metadata/exports.json').read_text())['archives']
            self.assertEqual({row['platform'] for row in exports},set(platforms.split(',')))
            self.assertEqual(len({row['sha256'] for row in exports}),3)

    def test_test_failure_and_unknown_comparison_fail_without_exporting(self):
        for code,status,phase in [('7','missing','test'),('0','unobservable','compare')]:
            with tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                result=self.pipeline(root,code,status)
                self.assertNotEqual(result.returncode,0)
                record=json.loads((root/'metadata/linux_amd64/result.json').read_text())
                self.assertEqual(record['phase'],phase)
                self.assertNotEqual(record['exit_code'],0)
                self.assertEqual(json.loads((root/'metadata/exports.json').read_text())['archives'],[])

    def test_actual_and_image_label_versions_must_match_build_metadata(self):
        for actual,label in [('2.0','1.0'),('1.0','2.0'),('1.0',''),('unknown','1.0')]:
            with self.subTest(actual=actual,label=label), tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                result=self.pipeline(root,test_version=actual,image_version=label)
                self.assertNotEqual(result.returncode,0)
                record=json.loads((root/'metadata/linux_amd64/result.json').read_text())
                self.assertEqual(record['phase'],'version')
                self.assertNotEqual(record['exit_code'],0)
                self.assertEqual(json.loads((root/'metadata/exports.json').read_text())['archives'],[])
                self.assertEqual(list((root/'output').iterdir()),[])

    def monitor_probe(self,root,fail_stage='',probe_output='version=1.0',probe_exit='0',missing=False,platforms='linux/amd64,linux/arm64'):
        tools=root/'bin'
        tools.mkdir()
        work=root/'application/fixture'
        (work/'meta-app').mkdir(parents=True)
        if not missing:
            (work/'meta-app/meta-app.sh').write_text('echo fixture\n')
        docker=tools/'docker'
        docker.write_text('#!'+sys.executable+'\n'+textwrap.dedent("""
            import os,sys
            stage=sys.argv[1]
            with open(os.environ['CALLS'], 'a') as log:
                log.write(stage+'\\n')
            if stage=='exec':
                sys.stdout.buffer.write(bytes.fromhex(os.environ['PROBE_HEX'])+b'\\n')
                sys.exit(int(os.environ['PROBE_EXIT']))
            if stage==os.environ['FAIL_STAGE']:
                print('fixture '+stage+' failed',file=sys.stderr)
                sys.exit(7)
        """))
        docker.chmod(0o755)
        python=tools/'python3'
        python.write_text('#!/bin/sh\nexit "$MATERIALIZE_EXIT"\n')
        python.chmod(0o755)
        env=dict(os.environ,PATH=str(tools)+':'+os.environ['PATH'],CALLS=str(root/'calls'),
                 GITHUB_WORKSPACE=str(ROOT),GITHUB_OUTPUT=str(root/'output'),RUNNER_TEMP=str(root),
                 app_branch='fixture',tag_repo='latest',repo_dockerhub='example/image',platform_prefer='linux/amd64',
                 container_name='version-meta-app',arch_branch=platforms,base_image='fixture:base',
                 FAIL_STAGE=fail_stage,PROBE_HEX=probe_output.encode().hex(),PROBE_EXIT=probe_exit,
                 MATERIALIZE_EXIT='7' if fail_stage=='materialize' else '0')
        result=subprocess.run(['bash','-e','-o','pipefail'],input=script_for('fetch-versions','Collect version from meta-app scripts'),
                              env=env,cwd=work,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        return json.loads((root/'app-version/version-fixture.json').read_text())

    def test_monitor_success_preserves_version_and_platform_selection(self):
        for platforms,expected in [('linux/amd64,linux/arm64','linux/amd64'),('linux/arm64','linux/arm64')]:
            with self.subTest(platforms=platforms), tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                record=self.monitor_probe(root,probe_output='version=old\nversion=1.0=build',platforms=platforms)
                self.assertEqual((record['status'],record['version'],record['platform_used']),('success','1.0=build',expected))
                self.assertIn('rm',(root/'calls').read_text().splitlines())
                self.assertIn('version=1.0=build',(root/'app-version/probe-fixture.log').read_text())

    def test_monitor_failures_keep_status_and_do_not_trust_partial_versions(self):
        cases=[('materialize','0','materialize_failed'),('pull','0','pull_failed'),
               ('run','0','run_failed'),('cp','0','copy_failed'),('','7','probe_failed')]
        for stage,code,expected in cases:
            with self.subTest(stage=stage,code=code), tempfile.TemporaryDirectory() as directory:
                root=Path(directory)
                record=self.monitor_probe(root,fail_stage=stage,probe_output='version=9.9',probe_exit=code)
                self.assertEqual((record['status'],record['version']),(expected,'unknown'))
                self.assertIn('rm',(root/'calls').read_text().splitlines())

    def test_monitor_missing_and_invalid_versions_are_explicit(self):
        cases=[(True,'version=1.0','meta_app_missing'),(False,'','version_invalid'),
               (False,'version= UNKNOWN ','version_invalid'),(False,'version=null','version_invalid'),
               (False,'version=1.0\r','version_invalid'),(False,'version=1.0\0suffix','version_invalid')]
        for missing,output,status in cases:
            with self.subTest(missing=missing,output=output), tempfile.TemporaryDirectory() as directory:
                record=self.monitor_probe(Path(directory),missing=missing,probe_output=output)
                self.assertEqual((record['status'],record['version']),(status,'unknown'))

    def test_meta_probe_failure_cannot_emit_valid_platform_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'app/meta-app').mkdir(parents=True)
            (root/'app/meta-app/meta-app.sh').write_text('echo version=1.0\n')
            (root/'bin').mkdir()
            docker=root/'bin/docker'
            docker.write_text('#!/bin/sh\nif [ "$1" = exec ]; then echo version=1.0; exit 7; fi\nexit 0\n')
            docker.chmod(0o755)
            python=root/'bin/python3'
            python.write_text('#!/bin/sh\nexit 0\n')
            python.chmod(0o755)
            (root/'metadata').mkdir()
            env=dict(os.environ,PATH=str(root/'bin')+':'+os.environ['PATH'],PATH_app=str(root/'app'),
                     PATH_metadata=str(root/'metadata'),app_branch='fixture',tag_repo='latest',arch_branch='linux/amd64',
                     base_image='fixture:base',build_arg='')
            result=subprocess.run(['bash'],input=script_for('container-build','Probe Meta-app on every configured platform'),
                                  env=env,cwd=ROOT,capture_output=True,text=True)
            self.assertEqual(result.returncode,7,result.stderr)
            self.assertEqual(json.loads((root/'metadata/meta-app.json').read_text())['platforms'],[])

    def test_final_gate_rejects_missing_failed_or_skipped_stages(self):
        stages=['meta-app','buildx','registry','build','test-export','free-storage','compress','split','verify-outputs','report']
        steps={k:{'conclusion':'success'} for k in stages}
        script=script_for('container-build','Enforce complete Container acceptance')
        def check(data):
            return subprocess.run(['bash'],input=script,env=dict(os.environ,STEP_RESULTS=json.dumps(data)),capture_output=True,text=True)
        self.assertEqual(check(steps).returncode,0)
        for key in stages:
            for status in ['failure','skipped','cancelled']:
                self.assertNotEqual(check(dict(steps,**{key:{'conclusion':status}})).returncode,0)

    def test_manual_artifact_tool_remains_nonpublishing(self):
        manual=(ROOT/'.github/workflows/download_artifact.yml').read_text()
        self.assertIn('  download:',manual)
        self.assertIn('  pull-image:',manual)
        self.assertIn('verify_image_archive.py',manual)
        self.assertNotIn('docker push ',manual)
        self.assertNotIn('gh release ',manual)


if __name__ == '__main__':
    unittest.main()
