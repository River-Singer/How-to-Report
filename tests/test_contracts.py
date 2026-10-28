"""Behavioral contract tests; all fixtures are synthetic and temporary."""

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
SHARED = PROJECT / "skill-src" / "shared"
HELPER = SHARED / "scripts" / "validate_run.py"
SPEC = importlib.util.spec_from_file_location("report_contract_validator", HELPER)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def ref(identity, revision=1):
    return {"id": identity, "revision": revision}


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="report-contract-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        shutil.copytree(SHARED / "assets" / "examples" / "multi-graph", self.run)

    def read(self, filename):
        return json.loads((self.run / filename).read_text(encoding="utf-8"))

    def write(self, filename, value):
        (self.run / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

    def validate(self, changed=()):
        return VALIDATOR.validate_run(self.run, changed)

    def invalid(self, phrase):
        result = self.validate()
        self.assertFalse(result["valid"], result)
        self.assertIn(phrase, "\n".join(result["errors"]))
        return result

    def events(self, rows):
        (self.run / "events.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    def grant(self, event_id="grant-1", sequence=1, scope_id="optional-data", decision="grant"):
        return {"event_id": event_id, "sequence": sequence, "type": "consent_decision",
                "scope_id": scope_id, "decision": decision,
                "scope": "Synthetic resource collection", "user_message_ref": "synthetic-user-message"}

    def read_event(self, sequence=2, consent_event_id="grant-1", scope_id="optional-data"):
        return {"event_id": f"read-{sequence}", "sequence": sequence, "type": "resource_read",
                "scope_id": scope_id, "resource_ref": "synthetic-resource",
                "consent_event_id": consent_event_id}

    def seed_verified(self):
        semantic = self.read("semantic.json")
        node = semantic["nodes"][2]
        node.pop("verification_dispositions", None)
        node.pop("verification_scope", None)
        node.update(status="verified", verification_refs=["check-observation"])
        self.write("semantic.json", semantic)
        run = self.read("run.json")
        run["checks"] = [{"id":"check-observation", "target":ref(node["id"]), "status":"pass",
                          "method":"Synthetic comparison", "scope":"Recorded observation",
                          "detail_ref":"check-detail.md"}]
        (self.run / "check-detail.md").write_text("Synthetic evidence only.", encoding="utf-8")
        self.write("run.json", run)

    def test_verified_checks_require_explicit_conflict_disposition(self):
        self.seed_verified()
        semantic = self.read("semantic.json")
        node = next(n for n in semantic["nodes"] if n.get("status") == "verified")
        data = self.read("run.json")
        passing = next(c for c in data["checks"] if c["id"] in node["verification_refs"])
        conflict = deepcopy(passing); conflict.update(id="conflict", status="fail", scope="a paraphrase of the same scope")
        data["checks"].append(conflict); self.write("run.json", data)
        self.invalid("unresolved exact-target")
        data["checks"].reverse(); self.write("run.json", data)
        self.invalid("unresolved exact-target")
        node["verification_dispositions"] = [{"check_id":"conflict", "disposition":"resolved",
            "reason":"new documented review resolves the earlier failure", "detail_ref":passing["detail_ref"],
            "resolving_check_id":passing["id"]}]
        self.write("semantic.json", semantic)
        self.assertTrue(self.validate()["valid"], self.validate())
        node["verification_dispositions"][0]["resolving_check_id"]="unknown"
        self.write("semantic.json", semantic); self.invalid("resolving_check_id")

    def test_different_scope_is_explicit_not_prose_similarity(self):
        self.seed_verified()
        semantic = self.read("semantic.json")
        node = next(n for n in semantic["nodes"] if n.get("status") == "verified")
        data = self.read("run.json")
        passing = next(c for c in data["checks"] if c["id"] in node["verification_refs"])
        data["checks"].append({**passing, "id":"other", "status":"not_assessable", "scope":"different stated scope"})
        self.write("run.json", data); self.invalid("unresolved exact-target")
        node["verification_dispositions"]=[{"check_id":"other","disposition":"different_scope",
            "reason":"outside the declared verification scope","detail_ref":passing["detail_ref"]}]
        self.write("semantic.json", semantic); self.invalid("verification_scope")
        node["verification_scope"]="Only the bounded observation, not general benefits"
        self.write("semantic.json", semantic); self.assertTrue(self.validate()["valid"], self.validate())
        node["verification_dispositions"].append(node["verification_dispositions"][0])
        self.write("semantic.json", semantic); self.invalid("unique exact-target")

    def test_conflict_on_other_exact_revision_does_not_block_verified_node(self):
        self.seed_verified()
        semantic=self.read("semantic.json")
        node=next(n for n in semantic["nodes"] if n.get("status")=="verified")
        other=deepcopy(node); other.update(revision=2,status="disputed",verification_refs=[])
        semantic["nodes"].append(other);self.write("semantic.json",semantic)
        data=self.read("run.json");passing=next(c for c in data["checks"] if c["id"] in node["verification_refs"])
        data["checks"].append({**passing,"id":"other-revision","status":"fail","target":ref(node["id"],2)})
        self.write("run.json",data);self.assertTrue(self.validate()["valid"],self.validate())

    def test_unfinished_check_requires_explicit_withdrawal_and_actual_detail(self):
        self.seed_verified()
        data = self.read("run.json")
        data["checks"].append({**data["checks"][0], "id":"unfinished", "status":"not_run"})
        self.write("run.json", data)
        self.invalid("unresolved exact-target")
        semantic = self.read("semantic.json")
        node = semantic["nodes"][2]
        node["verification_dispositions"] = [{"check_id":"unfinished", "disposition":"withdrawn",
            "reason":"Duplicate review task cancelled; actual completed check retained", "detail_ref":"withdrawal.md"}]
        self.write("semantic.json", semantic)
        self.invalid("withdrawal.md")
        (self.run / "withdrawal.md").write_text("", encoding="utf-8")
        self.invalid("nonempty supporting detail")
        (self.run / "withdrawal.md").write_text("Synthetic withdrawal justification", encoding="utf-8")
        self.assertTrue(self.validate()["valid"], self.validate())

    def test_malformed_dispositions_and_context_are_invalid_data(self):
        self.seed_verified()
        for value in (None, {}, [None], [{"check_id":[]}], [{"check_id":"check-observation", "disposition":[]} ]):
            semantic = self.read("semantic.json")
            semantic["nodes"][2]["verification_dispositions"] = value
            self.write("semantic.json", semantic)
            self.assertFalse(self.validate()["valid"])
        self.seed_verified()
        for value in (None, [], {"version":[],"target":[]},
                      {"version":"0.1","target":ref("a-blueprint"),"decision_id":"id","reason":"reason"}):
            data = self.read("run.json"); data["decision_context"] = value; self.write("run.json",data)
            self.assertFalse(self.validate()["valid"])

    def test_shipped_examples_are_valid_without_inventing_verification(self):
        self.assertTrue(self.validate()["valid"])
        foreign = SHARED / "assets" / "examples" / "foreign-audit"
        self.assertFalse((foreign / "semantic.json").exists())
        self.assertFalse((foreign / "tasks.json").exists())
        result = VALIDATOR.validate_run(foreign)
        self.assertTrue(result["valid"], result)
        data = json.loads((foreign / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(data["checks"][0]["status"], "not_assessable")

    def test_exact_impact_is_read_only_and_excludes_semantic_only_branch(self):
        before = {p.relative_to(self.run): p.read_bytes() for p in self.run.rglob("*") if p.is_file()}
        result = self.validate([("s-pilot", 1)])
        self.assertTrue(result["valid"], result)
        self.assertEqual({item["id"] for item in result["affected"]}, {
            "t-inspect", "t-baseline", "f-recorded", "c-pilot", "u-main", "m-summary",
            "b-compare", "p-overview", "a-blueprint"})
        self.assertEqual(before, {p.relative_to(self.run): p.read_bytes() for p in self.run.rglob("*") if p.is_file()})

    def test_new_revision_does_not_silently_replace_old_dependencies(self):
        data = self.read("run.json")
        later = deepcopy(data["sources"][0])
        later["revision"] = 2
        data["sources"].append(later)
        self.write("run.json", data)
        self.assertEqual(self.validate([("s-pilot", 2)])["affected"], [])
        self.assertTrue(self.validate([("s-pilot", 1)])["affected"])

    def test_prerequisites_and_result_ownership_are_not_impact_edges(self):
        data = self.read("tasks.json")
        data["tasks"][1]["input_refs"] = []
        self.write("tasks.json", data)
        result = self.validate([("t-inspect", 1)])
        self.assertNotIn("t-baseline", {item["id"] for item in result["affected"]})
        self.assertNotIn("t-inspect", {item["id"] for item in self.validate([("f-recorded", 1)])["affected"]})

    def test_unknown_exact_version_and_missing_revision_are_rejected(self):
        data = self.read("semantic.json")
        data["nodes"][2]["uses"] = [ref("s-pilot", 9)]
        self.write("semantic.json", data)
        self.invalid("unknown exact object version s-pilot@9")
        data["nodes"][2]["uses"] = [{"id": "s-pilot"}]
        self.write("semantic.json", data)
        self.invalid("positive integer")
        result = self.validate([("missing", 1)])
        self.assertFalse(result["valid"])
        self.assertIn("--changed", "\n".join(result["errors"]))

    def test_revisions_do_not_coerce_booleans_or_other_types(self):
        data = self.read("run.json")
        for value in (True, False, 0, -1, "1", 1.5, None, []):
            with self.subTest(value=value):
                data["sources"][0]["revision"] = value
                self.write("run.json", data)
                self.invalid("positive integer")

    def test_duplicate_identity_and_cross_kind_reuse_fail(self):
        data = self.read("run.json")
        data["sources"].append(deepcopy(data["sources"][0]))
        self.write("run.json", data)
        self.invalid("duplicate object version")
        data["sources"].pop()
        self.write("run.json", data)
        semantic = self.read("semantic.json")
        semantic["nodes"].append({"id": "s-pilot", "revision": 2, "kind": "source", "text": "A semantic node is not a source record."})
        self.write("semantic.json", semantic)
        self.invalid("changes kind")

    def test_unknown_contract_and_wrong_run_header_fail(self):
        data = self.read("run.json")
        data["contract_version"] = "99.0"
        self.write("run.json", data)
        self.invalid("unsupported version")
        data["contract_version"] = "0.1"
        self.write("run.json", data)
        semantic = self.read("semantic.json")
        semantic["run_id"] = "another-run"
        self.write("semantic.json", semantic)
        self.invalid("does not match")

    def test_node_text_exclusivity_and_status(self):
        data = self.read("semantic.json")
        data["nodes"][0]["text_ref"] = "run.md"
        self.write("semantic.json", data)
        self.invalid("exactly one")
        del data["nodes"][0]["text_ref"]
        data["nodes"][0]["status"] = "completed"
        self.write("semantic.json", data)
        self.invalid("expected one of")

    def test_task_completion_criteria_are_required(self):
        data = self.read("tasks.json")
        for value in (None, "", "   ", False):
            with self.subTest(value=value):
                data["tasks"][0]["completion"] = value
                self.write("tasks.json", data)
                self.invalid("completion: expected a nonempty string")

    def test_semantic_cycle_is_legal_but_task_cycle_is_not(self):
        self.assertTrue(self.validate()["valid"])  # Competing hypotheses link to each other.
        data = self.read("tasks.json")
        data["tasks"][0]["prerequisites"] = [ref("t-baseline")]
        self.write("tasks.json", data)
        self.invalid("execution prerequisite cycle")

    def test_prerequisites_must_reference_tasks(self):
        data = self.read("tasks.json")
        data["tasks"][0]["prerequisites"] = [ref("s-pilot")]
        self.write("tasks.json", data)
        self.invalid("not a task version")

    def test_verified_requires_matching_declared_check_not_completed_task(self):
        data = self.read("semantic.json")
        data["nodes"][2]["status"] = "verified"
        self.write("semantic.json", data)
        self.invalid("verified needs a matching pass check")
        run = self.read("run.json")
        run["checks"] = [{"id": "check-observation", "target": ref("f-recorded"), "status": "pass",
                          "method": "Synthetic source comparison", "scope": "Recorded values only",
                          "detail_ref": "check-detail.md"}]
        (self.run / "check-detail.md").write_text("Synthetic check declaration, not a claim about real-world truth.", encoding="utf-8")
        self.write("run.json", run)
        data["nodes"][2]["verification_refs"] = ["check-observation"]
        self.write("semantic.json", data)
        self.assertTrue(self.validate()["valid"])
        run["checks"][0]["target"] = ref("c-pilot")
        self.write("run.json", run)
        self.invalid("verified needs a matching pass check")

    def test_check_references_are_unique_ids_and_pass_has_supporting_detail(self):
        data = self.read("semantic.json")
        data["nodes"][0]["verification_refs"] = ["missing", "missing"]
        self.write("semantic.json", data)
        self.invalid("duplicate check ID")
        self.invalid("unknown check missing")
        data["nodes"][0]["verification_refs"] = [ref("check-x")]
        self.write("semantic.json", data)
        self.invalid("expected a nonempty string")
        del data["nodes"][0]["verification_refs"]
        self.write("semantic.json", data)
        run = self.read("run.json")
        run["checks"] = [{"id": "check-x", "target": ref("s-pilot"), "status": "pass", "detail_ref": "empty.md"}]
        (self.run / "empty.md").write_text("", encoding="utf-8")
        self.write("run.json", run)
        errors = "\n".join(self.invalid("nonempty supporting detail")["errors"])
        self.assertIn(".method", errors)
        self.assertIn(".scope", errors)

    def test_permission_grant_read_revoke_read_fails_and_new_grant_restores(self):
        self.events([self.grant(), self.read_event()])
        self.assertTrue(self.validate()["valid"])
        rows = [self.grant(), self.read_event(), self.grant("revoke-1", 3, decision="revoke"), self.read_event(4)]
        self.events(rows)
        self.invalid("current active grant")
        rows[-1:] = [self.grant("grant-2", 4), self.read_event(5, "grant-2")]
        self.events(rows)
        self.assertTrue(self.validate()["valid"])
        rows[-1]["consent_event_id"] = "grant-1"
        self.events(rows)
        self.invalid("current active grant")

    def test_denial_wrong_scope_missing_grant_and_missing_user_message_fail(self):
        variants = [
            [self.read_event()],
            [self.grant(decision="deny"), self.read_event()],
            [self.grant(), self.read_event(scope_id="another-scope")],
        ]
        for rows in variants:
            with self.subTest(rows=rows):
                self.events(rows)
                self.invalid("current active grant")
        grant = self.grant()
        del grant["user_message_ref"]
        self.events([grant, self.read_event()])
        self.invalid("user_message_ref")

    def test_event_sequence_and_identity_are_checked(self):
        row = self.grant()
        self.events([row, deepcopy(row)])
        errors = "\n".join(self.invalid("duplicate event ID")["errors"])
        self.assertIn("strictly increase", errors)

    def test_unhashable_enum_and_event_values_return_invalid_without_crashing(self):
        data = self.read("run.json")
        data["mode"] = []
        data["work_status"] = {}
        self.write("run.json", data)
        self.invalid("expected one of")
        self.events([{"event_id": "bad", "sequence": 1, "type": {}}])
        self.invalid("type: expected a nonempty string")
        row = self.grant()
        row["decision"] = []
        self.events([row])
        self.invalid("decision: expected one of")

    def test_invalid_json_duplicate_keys_and_invalid_utf8_are_data_errors(self):
        (self.run / "semantic.json").write_text('{"contract_version":"0.1","contract_version":"0.1"}', encoding="utf-8")
        self.invalid("duplicate JSON key")
        (self.run / "events.jsonl").write_bytes(b"\xff\xfe")
        self.invalid("invalid UTF-8")

    def test_owned_refs_cannot_escape_and_missing_files_fail(self):
        data = self.read("run.json")
        (self.root / "outside.md").write_text("Synthetic outside file", encoding="utf-8")
        data["notes_ref"] = "../outside.md"
        self.write("run.json", data)
        self.invalid("escapes the Run directory")
        data["notes_ref"] = "missing.md"
        self.write("run.json", data)
        self.invalid("local file does not exist")

    def test_local_hash_checks_real_bytes_and_remote_locator_is_not_fetched(self):
        data = self.read("run.json")
        data["sources"][0]["content_hash"] = hashlib.sha256((self.run / "inputs/pilot.md").read_bytes()).hexdigest()
        self.write("run.json", data)
        self.assertTrue(self.validate()["valid"])
        (self.run / "inputs/pilot.md").write_text("Changed synthetic bytes", encoding="utf-8")
        self.invalid("differ from declared hash")
        del data["sources"][0]["content_hash"]
        data["sources"][0]["ref"] = "https://example.invalid/never-fetched"
        self.write("run.json", data)
        self.assertTrue(self.validate()["valid"])
        data["sources"][0]["ref"] = "https://[invalid"
        self.write("run.json", data)
        self.invalid("invalid resource locator")

    def cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(HELPER), *map(str, args)], cwd=self.root,
                              capture_output=True, text=True, encoding="utf-8")

    def test_cli_unrelated_cwd_repeatable_changed_and_exit_codes(self):
        result = self.cli(self.run, "--changed", "s-pilot@1", "--changed", "s-background@1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("f-background", {item["id"] for item in json.loads(result.stdout)["affected"]})
        missing = self.cli(self.root / "absent")
        self.assertEqual(missing.returncode, 2)
        self.assertFalse(json.loads(missing.stdout)["valid"])
        malformed = self.cli(self.run, "--changed", "s-pilot")
        self.assertEqual(malformed.returncode, 2)
        invalid = self.cli(self.run, "--changed", "s-pilot@99")
        self.assertEqual(invalid.returncode, 1)
        self.assertFalse(json.loads(invalid.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
