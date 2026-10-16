#!/usr/bin/env python3
import copy
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

class MaterializeTests(unittest.TestCase):
    def newroot(self,folder):
        root=Path(folder)
        shutil.copyfile(ROOT/'README.md', root/'README.md')
        return root

    def test_declared_profiles_are_config_only(self):
        configured=hooks.profiles(ROOT)
        self.assertEqual(set(configured), {'aria2','curl','privoxy','squid','dnscrypt-proxy'})
        for app, profile in configured.items():
            self.assertTrue(catalog.validate_image_probe(app,profile))

    def test_generate_all_five_idempotently(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.newroot(d)
            for app in hooks.profiles(root):
                self.assertEqual(hooks.materialize(root,app),'generated')
                self.assertEqual(hooks.materialize(root,app),'unchanged')
                content=(root/'application'/app/'test'/'test.sh').read_text()
                self.assertIn('set -- ',content)
                self.assertIn('version=',content)

    def test_refuse_to_overwrite_foreign_script(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.newroot(d)
            path=root/'application'/'aria2'/'test'/'test.sh'
            path.parent.mkdir(parents=True)
            path.write_text('#!/bin/sh\necho legacy\n')
            with self.assertRaisesRegex(ValueError,'Refusing'):
                hooks.materialize(root,'aria2')
            self.assertEqual(path.read_text(),'#!/bin/sh\necho legacy\n')

    def test_nonshared_app_requires_existing_hook(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.newroot(d)
            with self.assertRaisesRegex(ValueError,'Non-declarative'):
                hooks.materialize(root,'nonexistent')

    def test_generated_wrapper_executes_identical_probe(self):
        with tempfile.TemporaryDirectory() as d:
            root=self.newroot(d)
            path=Path(d)/'mock'
            path.mkdir()
            (path/'aria2c').write_text('#!/bin/sh\nprintf "aria2 version 1.37.0\\n"\n')
            (path/'aria2c').chmod(0o755)
            hooks.materialize(root,'aria2')
            env=dict(os.environ,PATH=str(path)+os.pathsep+os.environ.get('PATH',''))
            wrapper=subprocess.run(['sh',str(root/'application'/'aria2'/'test'/'test.sh')],
                                   capture_output=True,text=True,env=env,check=True)
            old=subprocess.run(['sh',str(ROOT/'scripts'/'ci'/'probe-image.sh'),'aria2'],
                               capture_output=True,text=True,env=env,check=True)
            self.assertEqual(wrapper.stdout,old.stdout)
            self.assertEqual(wrapper.stdout,'version=1.37.0\n')

    def test_invalid_argv_and_extractor_rejected(self):
        cfg=hooks.profiles(ROOT)['aria2']
        for field,value in [('argv',['sh','-c','echo hacked']),('extract',{'kind':'eval'})]:
            clone=copy.deepcopy(cfg)
            clone[field]=value
            with self.assertRaisesRegex(ValueError,'image_probe'):
                hooks.generate('aria2',clone)

if __name__=='__main__':
    unittest.main(verbosity=2)
