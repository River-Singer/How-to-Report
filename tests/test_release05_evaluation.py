"""New evaluation inputs remain staged, portable and explicitly unexecuted."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
import unittest

sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[1]/'evaluation'
spec=importlib.util.spec_from_file_location('release05_cases_check',ROOT/'tools/validate_cases.py')
CHECK=importlib.util.module_from_spec(spec)
spec.loader.exec_module(CHECK)


class Release05EvaluationTests(unittest.TestCase):
    def test_previous_catalog_bytes_preserved(self):
        expected={'eval-cases.jsonl':'e25e5a563b89f29f193e1da110abc3777f7f9e417a10de2ed9c1b31fe169eb1e','behavior-cases.jsonl':'53a25179fe9231f11957d3c7ec93a55762e7d4421da8b72f8636449412343985'}
        for name,digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest)

    def test_new_cases_have_real_inputs_and_staged_change(self):
        cases,issues=CHECK.validate(ROOT)
        self.assertEqual(issues,[])
        new=[x for x in cases if x['id'].startswith('V05-')]
        self.assertEqual(len(new),12)
        for case in new:
            self.assertEqual(len(case['turns']),2)
            before=CHECK.visible_turn(case,1)
            after=CHECK.visible_turn(case,2)
            self.assertNotEqual(before['prompt'],after['prompt'])
            self.assertNotIn('must',before)
            self.assertNotIn('must_not',after)
            self.assertTrue(before['fixtures'])
            for fixture in before['fixtures']:
                self.assertGreater((ROOT/fixture).stat().st_size,0)
        self.assertEqual(json.loads((ROOT/'dataset.json').read_text(encoding='utf-8'))['status'],'prepared_not_run')

    def test_spacing_case_has_actual_editable_target(self):
        cases,issues=CHECK.validate(ROOT)
        self.assertFalse(issues)
        case=next(x for x in cases if x['id']=='V05-SCOPE')
        self.assertIn('fixtures/release05/spacing-target.html',case['fixtures'])
        html=(ROOT/'fixtures/release05/spacing-target.html').read_text(encoding='utf-8')
        self.assertIn('gap:18px',html)
        self.assertIn('synthetic-spacing@1',html)


if __name__=='__main__':unittest.main()
