"""0.9.1 input structure, staged exposure and portable hashes; no model calls."""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / 'evaluation/content-0.9.1'
spec = importlib.util.spec_from_file_location('content_091_checker', ROOT / 'evaluation/tools/validate_cases.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
COUNTS = [2, 1, 3, 1, 2, 3, 4, 2, 3, 2, 1, 2, 3, 4, 3, 2, 1, 2]


class Content091Tests(unittest.TestCase):
    def cases(self):
        rows, errors = checker.validate(CURRENT)
        self.assertFalse(errors)
        return rows

    def test_relocated_dataset_complete_readonly(self):
        with tempfile.TemporaryDirectory() as temp:
            moved = Path(temp) / 'input'
            shutil.copytree(CURRENT, moved)
            before = {p.relative_to(moved): p.read_bytes() for p in moved.rglob('*') if p.is_file()}
            rows, errors = checker.validate(moved)
            self.assertFalse(errors)
            self.assertEqual([len(row['turns']) for row in rows], COUNTS)
            self.assertEqual(len({row['id'] for row in rows}), 18)
            self.assertEqual(before, {p.relative_to(moved): p.read_bytes() for p in moved.rglob('*') if p.is_file()})

    def test_inventory_exact_and_fact_bytes_preserved(self):
        manifest = json.loads((CURRENT / 'dataset.json').read_text(encoding='utf-8'))
        actual = {p.relative_to(CURRENT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in CURRENT.rglob('*') if p.is_file() and p.name != 'dataset.json'}
        self.assertEqual(actual, manifest['files'])
        prior = ROOT / 'evaluation/content-0.9.0/fixtures'
        for p in prior.iterdir():
            self.assertEqual(p.read_bytes(), (CURRENT / 'fixtures' / p.name).read_bytes())

    def test_all_visible_turns_exact_projection(self):
        allowed = {'case_id', 'entry', 'environment', 'turn', 'prompt', 'fixtures', 'instructions'}
        for case in self.cases():
            self.assertEqual(set(case['fixtures']), {p for stage in case['turn_fixtures'] for p in stage})
            for n, prompt in enumerate(case['turns'], 1):
                result = checker.visible_turn(case, n)
                self.assertEqual(set(result), allowed)
                self.assertEqual(result['prompt'], prompt)
                self.assertEqual(result['fixtures'], case['turn_fixtures'][n - 1])

    def test_new_sources_have_delayed_exposure(self):
        cases = {case['id']: case for case in self.cases()}
        for identity, filename, first in [
            ('C091-DUAL-PROJECTS', 'dual-roles.md', 2),
            ('C091-DUAL-PROJECTS', 'dual-partial.md', 3),
            ('C091-MARKET-PRODUCT', 'product-records.md', 2),
            ('C091-MARKET-PRODUCT', 'campaign-records.md', 3),
            ('C091-SALES', 'sales-reply.md', 2),
        ]:
            case = cases[identity]
            path = 'fixtures/' + filename
            for n in range(1, first):
                self.assertNotIn(path, checker.visible_turn(case, n)['fixtures'])
            self.assertIn(path, checker.visible_turn(case, first)['fixtures'])

    def test_audit_body_first_and_old_scenarios_retained(self):
        rows = self.cases()
        prior = [json.loads(line) for line in (ROOT / 'evaluation/content-0.9.0/cases.jsonl').read_text(encoding='utf-8').splitlines()]
        for actual, original in zip(rows, prior):
            self.assertEqual(actual['family'], original['family'])
            self.assertEqual(actual['turn_fixtures'], original['turn_fixtures'])
            for prompt, old_prompt in zip(actual['turns'], original['turns']):
                self.assertEqual(prompt, old_prompt)
        audit = rows[12]
        self.assertEqual(checker.visible_turn(audit, 1)['fixtures'], ['fixtures/audit-draft.md'])
        self.assertEqual(audit['turns'][0], prior[12]['turns'][0])
        self.assertNotIn('fixtures/audit-author-notes.md', checker.visible_turn(audit, 2)['fixtures'])
        self.assertIn('fixtures/audit-author-notes.md', checker.visible_turn(audit, 3)['fixtures'])

    def test_tampering_detected_without_repair(self):
        with tempfile.TemporaryDirectory() as temp:
            moved = Path(temp) / 'input'
            shutil.copytree(CURRENT, moved)
            fixture = moved / 'fixtures/dual-roles.md'
            fixture.write_text('changed', encoding='utf-8')
            _, errors = checker.validate(moved)
            self.assertTrue(any('changed input' in error for error in errors))
            self.assertEqual(fixture.read_text(encoding='utf-8'), 'changed')


if __name__ == '__main__':
    unittest.main()
