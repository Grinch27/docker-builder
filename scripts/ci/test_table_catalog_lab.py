#!/usr/bin/env python3
"""Non-production strict Markdown data-store prototype tests."""
import copy
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'/'ci'))
import catalog
import table_catalog_lab as lab

class TableCatalogLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=(ROOT/'README.md').read_text(encoding='utf-8')
        cls.config=catalog.catalog_data_from_text(cls.text)
        cls.monitor=catalog.snapshot_from_readme(cls.text)

    def test_all_30_targets_and_24_observations_roundtrip(self):
        result=lab.compare_with_readme(ROOT/"README.md",catalog)
        self.assertEqual(result['apps'],24)
        self.assertEqual(result['targets'],30)
        self.assertEqual(result['observations'],24)
        self.assertEqual(result['table_columns'],17)

    def test_reject_duplicate_target(self):
        table=lab.render(self.config,self.monitor)
        row=table.splitlines()[2]
        with self.assertRaisesRegex(ValueError,"Duplicate target"):
            lab.parse(table+row+'\n')

    def test_reject_missing_and_excess_column(self):
        table=lab.render(self.config,self.monitor)
        lines=table.splitlines()
        fields=lab.parse_line(lines[2])
        lines[2]='| '+' | '.join(fields[:-1])+' |'
        with self.assertRaisesRegex(ValueError,"Missing or excess columns"):
            lab.parse('\n'.join(lines))

    def test_reject_inconsistent_monitor_on_same_app(self):
        table=lab.render(self.config,self.monitor)
        lines=table.splitlines()
        # adguardvpn-cli has three target rows; corrupt the second one's version.
        row=lab.parse_line(lines[3])
        row[15]='poisoned-version'
        lines[3]='| '+' | '.join(lab.encode(v) for v in row)+' |'
        with self.assertRaisesRegex(ValueError,"Conflicting per-app monitoring metadata"):
            lab.parse('\n'.join(lines))

    def test_escaped_pipe_roundtrip(self):
        self.assertEqual(lab.parse_line('| one\\|two | three\\\\four |'),['one|two','three\\four'])
        with self.assertRaisesRegex(ValueError,"Unknown Markdown cell escape"):
            lab.parse_line('| one\\x |')

if __name__=="__main__":
    unittest.main(verbosity=2)
