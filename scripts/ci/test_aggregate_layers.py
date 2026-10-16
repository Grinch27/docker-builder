#!/usr/bin/env python3
import json
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'/'ci'))
import importlib.util
spec=importlib.util.spec_from_file_location('agg',ROOT/'scripts'/'ci'/'aggregate-layer-artifacts.py')
agg=importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)

class AggregateTests(unittest.TestCase):
    def test_deduplicate_layers_across_images(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            for name,layers in [("a",["sha256:1","sha256:2"]),("b",["sha256:2","sha256:3"])]:
                folder=p/("layers-"+name);folder.mkdir()
                (folder/("layer-"+name+".json")).write_text(json.dumps({"image_name":name,"Layers":layers}))
            self.assertEqual(len(agg.aggregate(p)),2)
            self.assertEqual(set(sum(agg.aggregate(p).values(),[])),{"sha256:1","sha256:2","sha256:3"})
    def test_missing_and_conflicting_artifacts_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            with self.assertRaisesRegex(ValueError,"No per-image"): agg.aggregate(p)
            (p/"layer-one.json").write_text(json.dumps({"image_name":"a","Layers":["l1"]}))
            (p/"layer-two.json").write_text(json.dumps({"image_name":"a","Layers":["l2"]}))
            with self.assertRaisesRegex(ValueError,"Conflicting layer"): agg.aggregate(p)

if __name__=="__main__": unittest.main()

