"""Budget, version invalidation and actual-evidence release regressions."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "skill-src/how-to-report/scripts"
sys.path.insert(0, str(SOURCE))
SPEC = importlib.util.spec_from_file_location("presentation_controller_test_core", SOURCE / "presentation_controller.py")
control = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(control)


def sample():
    return {"schema_version": "0.1", "project_id": "p", "revision": 1,
            "brief": {}, "facts": {}, "pages": [], "sources": []}


class PresentationControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.artifact = self.directory / "deck.pptx"
        self.artifact.write_bytes(b"actual-artifact-bytes")
        self.detail = self.directory / "check.md"
        self.detail.write_text("Executed check of the actual target. Result passed.", encoding="utf-8")
        self.document = sample()
        self.state = control.new_control_state(self.document, max_calls=2, max_repairs=1,
                                                max_seconds=100, required_checks=["build", "visual"], now=100)

    def tearDown(self):
        self.temp.cleanup()

    def checked(self):
        state = control.bind_artifact(self.state, self.artifact)
        for identifier in ("build", "visual"):
            state = control.record_check(state, identifier, "pass", "check.md",
                                         method="actual-target-inspection", scope="current artifact",
                                         detail_path=self.detail)
        return state

    def test_budget_reservations_and_results_are_idempotent(self):
        before = deepcopy(self.state)
        state = control.reserve_call(self.state, "one", "build", now=101)
        self.assertEqual(self.state, before)
        self.assertEqual(control.reserve_call(state, "one", "build", now=102), state)
        with self.assertRaisesRegex(ValueError, "another kind"):
            control.reserve_call(state, "one", "render", now=102)
        state = control.record_call(state, "one", {"exit_code": 0}, now=103)
        self.assertEqual(control.record_call(state, "one", {"exit_code": 0}, now=104), state)
        with self.assertRaisesRegex(ValueError, "another result"):
            control.record_call(state, "one", {"exit_code": 1}, now=104)
        state = control.reserve_call(state, "two", "render", now=105)
        with self.assertRaisesRegex(ValueError, "call budget"):
            control.reserve_call(state, "three", "review", now=106)
        with self.assertRaisesRegex(ValueError, "deadline"):
            control.reserve_call(self.state, "late", "build", now=200)

    def test_ready_requires_all_current_checks_and_actual_evidence(self):
        self.assertEqual(control.evaluate_release(self.state, now=101)["status"], "failed")
        bound = control.bind_artifact(self.state, self.artifact)
        self.assertEqual(control.evaluate_release(bound, now=101)["status"], "draft")
        state = self.checked()
        self.assertEqual(control.evaluate_release(state, self.document, now=101)["status"], "ready")
        state = control.record_check(state, "extra", "not_assessable", "check.md", detail_path=self.detail)
        self.assertEqual(control.evaluate_release(state, now=101)["status"], "draft")
        self.detail.write_text("Changed after checking", encoding="utf-8")
        report = control.evaluate_release(state, now=101)
        self.assertTrue(any("evidence changed" in reason for reason in report["reasons"]))

    def test_default_release_requires_template_and_dataviz_review(self):
        state = control.new_control_state(self.document, now=100)
        self.assertIn("template-and-dataviz", state["required_checks"])
        state = control.bind_artifact(state, self.artifact)
        for identifier in state["required_checks"]:
            if identifier != "template-and-dataviz":
                state = control.record_check(state, identifier, "pass", "check.md",
                                             method="actual-target-inspection", scope="current artifact",
                                             detail_path=self.detail)
        report = control.evaluate_release(state, self.document, now=101)
        self.assertEqual(report["status"], "draft")
        self.assertIn("required check not_run: template-and-dataviz", report["reasons"])
        state = control.record_check(state, "template-and-dataviz", "pass", "check.md",
                                     method="page-level template and data-visualization review",
                                     scope="current artifact, source facts and available template candidates",
                                     detail_path=self.detail)
        self.assertEqual(control.evaluate_release(state, self.document, now=101)["status"], "ready")

    def test_persisted_and_explicit_required_checks_keep_their_scope(self):
        self.assertEqual(self.state["required_checks"], ["build", "visual"])
        self.assertEqual(control.evaluate_release(self.checked(), now=101)["status"], "ready")
        legacy = control.new_control_state(self.document, now=100)
        legacy["required_checks"] = ["build", "target_render", "content_review", "visual_review", "editability"]
        legacy = control.bind_artifact(legacy, self.artifact)
        for identifier in legacy["required_checks"]:
            legacy = control.record_check(legacy, identifier, "pass", "check.md",
                                          method="actual-target-inspection", scope="persisted checklist",
                                          detail_path=self.detail)
        self.assertEqual(control.evaluate_release(legacy, now=101)["status"], "ready")

    def test_call_identity_cannot_be_reused_after_document_change(self):
        state = control.reserve_call(self.state, "build-once", "build", now=101)
        changed = deepcopy(self.document)
        changed["revision"] = 2
        state = control.sync_document(state, changed)
        with self.assertRaisesRegex(ValueError, "another document version"):
            control.reserve_call(state, "build-once", "build", now=102)
        state = control.reserve_call(state, "build-again", "build", now=102)
        self.assertEqual(state["budget"]["calls_reserved"], 2)

    def test_artifact_and_document_changes_invalidate_checks(self):
        state = self.checked()
        changed = deepcopy(self.document)
        changed["revision"] = 2
        changed["brief"]["audience"] = "changed"
        self.assertEqual(control.evaluate_release(state, changed, now=101)["status"], "failed")
        synced = control.sync_document(state, changed)
        self.assertEqual(synced["budget"], state["budget"])
        synced = control.bind_artifact(synced, self.artifact)
        report = control.evaluate_release(synced, changed, now=101)
        self.assertEqual(report["status"], "draft")
        self.assertEqual(report["check_ids"], [])
        self.artifact.write_bytes(b"modified externally")
        self.assertEqual(control.evaluate_release(state, now=101)["status"], "failed")

    def test_blocker_carries_across_repair_and_requires_current_resolution(self):
        state = self.checked()
        state = control.record_finding(state, {"id": "overflow", "requirement": "main text readable",
            "evidence": "page 1 image", "impact": "text clipped", "acceptance": "all text visible"})
        self.assertEqual(control.evaluate_release(state, now=101)["status"], "draft")
        state = control.start_repair(state, "Correct text width", now=102)
        with self.assertRaisesRegex(ValueError, "repair budget"):
            control.start_repair(state, "Another repair", now=103)
        state = control.resolve_finding(state, "overflow", "visual", "Current image shows complete text")
        self.assertEqual(control.evaluate_release(state, now=104)["status"], "ready")
        changed = deepcopy(self.document)
        changed["revision"] = 2
        state = control.sync_document(state, changed)
        state = control.bind_artifact(state, self.artifact)
        for identifier in ("build", "visual"):
            state = control.record_check(state, identifier, "pass", "check.md", method="recheck",
                                         scope="new revision", detail_path=self.detail)
        self.assertEqual(control.evaluate_release(state, now=104)["open_blockers"], ["overflow"])

    def test_missing_or_empty_details_cannot_create_pass(self):
        state = control.bind_artifact(self.state, self.artifact)
        with self.assertRaises(ValueError):
            control.record_check(state, "build", "pass", "check.md", detail_path=self.detail)
        empty = self.directory / "empty.md"
        empty.write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "empty"):
            control.record_check(state, "build", "pass", "empty.md", method="inspect",
                                 scope="current", detail_path=empty)
        state = control.record_check(state, "build", "fail", "check.md", detail_path=self.detail)
        with self.assertRaisesRegex(ValueError, "already records"):
            control.record_check(state, "build", "pass", "check.md", method="inspect",
                                 scope="current", detail_path=self.detail)

    def test_missing_persisted_deadline_is_invalid(self):
        state = deepcopy(self.state)
        state["budget"].pop("deadline")
        with self.assertRaisesRegex(ValueError, "deadline"):
            control.reserve_call(state, "one", "build", now=101)


if __name__ == "__main__":
    unittest.main()
