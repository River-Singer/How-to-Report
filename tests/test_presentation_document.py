"""Regression checks for presentation facts, bindings and immutable revisions."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "skill-src/how-to-report/scripts"
SPEC = importlib.util.spec_from_file_location("presentation_document_test_core", SOURCE / "presentation_document.py")
doc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doc)


def sample():
    return {
        "schema_version": "0.1", "project_id": "feishu", "revision": 1,
        "brief": {"audience": "IT领导"}, "sources": [{"id": "source-docx", "ref": "input.docx"}],
        "facts": {
            "purchased": {"value": 17300, "source_ref": "source-docx"},
            "allocated": {"value": 17048}, "activated": {"value": 8972},
            "gap": {"derived": {"op": "difference", "args": ["allocated", "activated"]}},
            "rate": {"derived": {"op": "ratio", "args": ["activated", "allocated"]}},
        },
        "pages": [
            {"id": "overview", "kind": "scene", "elements": [
                {"id": "overview-title", "type": "text", "text": ["激活 ", {"ref": "rate", "format": "percent"}]}]},
            {"id": "comparison", "kind": "scene", "elements": [
                {"id": "comparison-data", "type": "chart", "values": [{"ref": "allocated"}, {"ref": "gap"}]}]},
            {"id": "unchanged", "kind": "scene", "elements": []},
        ], "relations": [], "locks": [], "output_contract": {},
    }


class PresentationDocumentTests(unittest.TestCase):
    def test_fact_evaluation_and_cross_page_binding(self):
        document = sample()
        before = deepcopy(document)
        doc.validate_document(document)
        facts = doc.evaluate_facts(document)
        self.assertEqual(facts["gap"], 8076)
        self.assertEqual(doc.resolve_text(document["pages"][0]["elements"][0]["text"], facts), "激活 52.6%")
        self.assertEqual(doc.resolve_value({"ref": "allocated"}, facts), 17048)
        self.assertEqual(doc.resolve_value({"ref": "allocated", "format": "integer"}, facts), "17,048")
        self.assertEqual(document, before)

    def test_arithmetic_operators_and_scale(self):
        document = sample()
        document["facts"].update(total={"derived": {"op": "sum", "args": ["allocated", "gap"]}},
                                 times={"derived": {"op": "product", "args": ["activated", "gap"], "scale": 0.01}})
        facts = doc.evaluate_facts(document)
        self.assertEqual(facts["total"], 25124)
        self.assertAlmostEqual(facts["times"], 724578.72)
        self.assertEqual(doc.resolve_text({"text": {"ref": "rate", "format": ".2%"}, "weight": 700}, facts), "52.63%")

    def test_unknown_references_and_division_by_zero(self):
        document = sample()
        document["facts"]["allocated"]["value"] = 0
        with self.assertRaisesRegex(ValueError, "division by zero"):
            doc.evaluate_facts(document)
        document = sample()
        document["pages"][0]["elements"][0]["text"] = {"ref": "missing"}
        with self.assertRaisesRegex(ValueError, "unknown fact reference"):
            doc.validate_document(document)

    def test_cycle_nonfinite_boolean_and_duplicate_ids(self):
        document = sample()
        document["facts"]["allocated"] = {"derived": {"op": "sum", "args": ["gap"]}}
        with self.assertRaisesRegex(ValueError, "cyclic"):
            doc.evaluate_facts(document)
        for value in (True, float("inf"), float("nan")):
            document = sample()
            document["facts"]["allocated"]["value"] = value
            with self.assertRaises(ValueError):
                doc.validate_document(document)
        document = sample()
        document["revision"] = True
        with self.assertRaisesRegex(ValueError, "positive integer"):
            doc.validate_document(document)
        document = sample()
        document["pages"][0]["elements"][0]["id"] = "allocated"
        with self.assertRaisesRegex(ValueError, "duplicate object ID"):
            doc.validate_document(document)

    def test_patch_is_immutable_recomputes_dependencies_and_replays(self):
        document = sample()
        before = deepcopy(document)
        operations = [{"op": "replace", "path": "/facts/activated/value", "value": 9000}]
        changed = doc.apply_patch_to_document(document, operations, 1, "change-activation")
        self.assertEqual(document, before)
        self.assertEqual(changed["revision"], 2)
        self.assertEqual(doc.evaluate_facts(changed)["gap"], 8048)
        self.assertEqual(changed["_patch_history"][-1]["affected_pages"], ["overview", "comparison"])
        self.assertEqual(doc.apply_patch_to_document(changed, operations, 1, "change-activation"), changed)
        later = doc.apply_patch_to_document(changed, [{"op": "add", "path": "/brief/topic", "value": "进展"}], 2, "add-topic")
        self.assertEqual(doc.apply_patch_to_document(later, operations, 1, "change-activation"), changed)
        with self.assertRaisesRegex(ValueError, "different patch"):
            doc.apply_patch_to_document(changed, [{"op": "replace", "path": "/facts/activated/value", "value": 9001}], 1, "change-activation")
        with self.assertRaisesRegex(ValueError, "revision conflict"):
            doc.apply_patch_to_document(changed, operations, 1, "another-operation")

    def test_patch_locks_and_pointer_operations(self):
        document = sample()
        document["locks"] = [{"path": "/brief/audience", "value": "IT领导"}]
        with self.assertRaisesRegex(ValueError, "violates lock"):
            doc.apply_patch_to_document(document, [{"op": "replace", "path": "/brief/audience", "value": "全体员工"}], 1, "wrong-audience")
        with self.assertRaisesRegex(ValueError, "violates lock"):
            doc.apply_patch_to_document(document, [{"op": "replace", "path": "/locks", "value": []}], 1, "remove-lock")
        changed = doc.apply_patch_to_document(document, [
            {"op": "test", "path": "/brief/audience", "value": "IT领导"},
            {"op": "add", "path": "/brief/a~1b", "value": "字段"},
            {"op": "add", "path": "/pages/-", "value": {"id": "appendix", "elements": []}},
        ], 1, "add-fields")
        self.assertEqual(changed["brief"]["a/b"], "字段")
        self.assertIn("appendix", changed["_patch_history"][-1]["affected_pages"])
        with self.assertRaisesRegex(ValueError, "managed field"):
            doc.apply_patch_to_document(document, [{"op": "replace", "path": "/revision", "value": 9}], 1, "bad-revision")

    def test_fact_metadata_change_invalidates_derived_consumers(self):
        document = sample()
        changed = doc.apply_patch_to_document(document,
            [{"op": "add", "path": "/facts/activated/period", "value": "2026-11-13"}], 1, "period-change")
        self.assertEqual(changed["_patch_history"][-1]["affected_pages"], ["overview", "comparison"])

    def test_relation_identity_and_type_are_checked(self):
        document = sample()
        document["relations"] = [{"id": "overview", "type": "comparison"}]
        with self.assertRaisesRegex(ValueError, "duplicate object ID"):
            doc.validate_document(document)
        document["relations"] = [{"id": "comparison-relation", "type": ""}]
        with self.assertRaisesRegex(ValueError, "relation.type"):
            doc.validate_document(document)

    def test_lock_preserves_json_value_types(self):
        document = sample()
        document["brief"]["limit"] = 1
        document["locks"] = [{"path": "/brief/limit", "value": 1}]
        with self.assertRaisesRegex(ValueError, "violates lock"):
            doc.apply_patch_to_document(document,
                [{"op": "replace", "path": "/brief/limit", "value": True}], 1, "boolean-limit")

    def test_declared_relation_endpoints_must_resolve(self):
        document = sample()
        document["relations"] = [{"id": "quantity-comparison", "type": "comparison",
                                  "from": "allocated", "to": "activated"}]
        doc.validate_document(document)
        document["relations"][0]["to"] = "missing"
        with self.assertRaisesRegex(ValueError, "unknown object ID"):
            doc.validate_document(document)
        del document["relations"][0]["to"]
        with self.assertRaisesRegex(ValueError, "both from and to"):
            doc.validate_document(document)


if __name__ == "__main__":
    unittest.main()
