"""Deterministic version/acceptance lifecycle tests; no model or case execution."""
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
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "skill-src" / "how-to-report"


class VersionLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="report-versions-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.package = self.root / "installed"
        shutil.copytree(SOURCE / "scripts", self.package / "scripts",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        shutil.copyfile(PROJECT / "skill-src/shared/scripts/validate_run.py", self.package / "scripts/validate_run.py")
        shutil.copyfile(PROJECT / "skill-src/shared/scripts/write_boundary.py", self.package / "scripts/write_boundary.py")
        shutil.copytree(SOURCE / "assets/report-run", self.package / "assets/report-run")
        self.run = self.root / "Run #1 50% 鐗堟湰"
        self.run.mkdir()
        self.file = self.root / "source #1 80% 鏁版嵁.txt"
        self.file.write_text("synthetic source bytes", encoding="utf-8")
        (self.run / "run.md").write_text("Synthetic scope: demonstrate mechanics, no factual claim.", encoding="utf-8")
        self.record = {"contract_version": "0.1", "run_id": "synthetic", "mode": "create", "work_status": "in_progress",
                       "notes_ref": "run.md", "sources": [], "artifacts": [], "checks": []}
        self.write(self.record)
        spec = importlib.util.spec_from_file_location("versions_under_test", self.package / "scripts/report_versions.py")
        self.helper = importlib.util.module_from_spec(spec)
        modules = {k: sys.modules.pop(k, None) for k in ("report_run", "validate_run", "write_boundary")}
        before, bytecode = sys.path[:], sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(self.helper)
        finally:
            sys.path[:], sys.dont_write_bytecode = before, bytecode
            for k, value in modules.items():
                sys.modules.pop(k, None)
                if value is not None:
                    sys.modules[k] = value

    def read(self):
        return json.loads((self.run / "run.json").read_text(encoding="utf-8"))

    def write(self, record):
        (self.run / "run.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def digest(self):
        return hashlib.sha256((self.run / "run.json").read_bytes()).hexdigest()

    def mutate(self, command, **kwargs):
        return self.helper.mutate(self.run, self.digest(), command, reason="Synthetic explicit decision.", **kwargs)

    def register(self, identity, revision=1, kind="source", uses=()):
        return self.mutate("register", identity=identity, revision=revision, kind=kind, file=self.file,
                           uses=uses, no_dependencies=not uses)

    def choose(self, identity, revision=1):
        return self.mutate("select", target=(identity, revision))

    def check(self, identity="a", revision=1, check_id="c1", status="pass"):
        data = self.read()
        path = self.run / (check_id + ".md")
        path.write_text("Actual synthetic test review fixture, not a model review.", encoding="utf-8")
        data["checks"].append({"id": check_id, "target": {"id": identity, "revision": revision},
                               "status": status, "detail_ref": path.name, "method": "fixture comparison", "scope": "synthetic bytes"})
        self.write(data)

    def accept(self, identity="a", revision=1, acceptance_id="accepted-1", check_ids=("c1",)):
        return self.mutate("accept", target=(identity, revision), acceptance_id=acceptance_id, check_ids=check_ids)

    def accepted(self):
        self.register("s")
        self.register("a", kind="artifact", uses=[("s", 1)])
        self.choose("s")
        self.choose("a")
        self.check()
        return self.accept()

    def test_registration_keeps_real_snapshot_history_and_no_implied_selection(self):
        before = (self.run / "run.json").read_bytes()
        result = self.register("s")
        record = self.read()
        source = record["sources"][0]
        self.assertEqual((self.run / source["ref"]).read_bytes(), self.file.read_bytes())
        self.assertEqual(source["content_hash"], hashlib.sha256(self.file.read_bytes()).hexdigest())
        self.assertEqual(source["origin"]["filename"], self.file.name)
        self.assertEqual(result["selections"], [])
        self.assertEqual(record["checks"], [])
        self.assertEqual([p.read_bytes() for p in (self.run / "versions/history").glob("*.json")], [before])
        self.file.unlink()
        self.assertTrue(self.helper.inspect(self.run)["valid"])

    def test_full_v1_to_v2_revision_retains_old_checks_and_fresh_acceptance(self):
        initial = self.accepted()
        self.assertEqual(initial["artifacts"][0]["acceptance_status"], "current")
        old_checks = deepcopy(self.read()["checks"])
        self.register("s", 2)
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "current")
        changed = self.choose("s", 2)
        self.assertEqual(changed["artifacts"][0]["acceptance_status"], "stale")
        self.assertEqual(changed["artifacts"][0]["currentness"]["state"], "pending")
        self.register("a", 2, "artifact", [("s", 2)])
        self.choose("a", 2)
        self.check(revision=2, check_id="c2")
        result = self.accept(revision=2, acceptance_id="accepted-2", check_ids=["c2"])
        self.assertEqual([x["acceptance_status"] for x in result["artifacts"]], ["stale", "current"])
        self.assertEqual(self.read()["checks"][0], old_checks[0])

    def test_new_highest_revision_does_not_replace_explicit_choice(self):
        self.accepted()
        self.register("s", 100)
        self.assertEqual(self.helper.inspect(self.run)["selections"][1]["target"]["revision"], 1)
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "current")

    def test_switch_back_does_not_revive_old_acceptance_or_allow_old_check(self):
        self.accepted()
        self.register("s", 2)
        self.choose("s", 2)
        self.choose("s", 1)
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")
        with self.assertRaisesRegex(ValueError, "fresh actual Check"):
            self.accept(acceptance_id="again")
        self.check(check_id="c2")
        self.assertEqual(self.accept(acceptance_id="again", check_ids=["c2"])["artifacts"][0]["acceptance_status"], "current")

    def test_check_detail_change_needs_fresh_check(self):
        self.accepted()
        (self.run / "c1.md").write_text("Changed review", encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")
        with self.assertRaisesRegex(ValueError, "fresh actual Check"):
            self.accept(acceptance_id="again")

    def test_scope_notes_change_stales_acceptance(self):
        self.accepted()
        (self.run / "run.md").write_text("Different scope", encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")

    def test_unrelated_branch_selection_does_not_stale_acceptance(self):
        self.accepted()
        self.register("independent")
        self.choose("independent")
        self.register("independent", 2)
        result = self.choose("independent", 2)
        self.assertEqual(result["artifacts"][0]["acceptance_status"], "current")

    def test_new_nonpass_check_blocks_current_acceptance_without_invalidating_structure(self):
        self.accepted()
        self.check(check_id="c2", status="not_assessable")
        result = self.helper.inspect(self.run)
        self.assertTrue(result["valid"])
        self.assertEqual(result["artifacts"][0]["acceptance_status"], "stale")
        with self.assertRaisesRegex(ValueError, "all registered checks"):
            self.accept(acceptance_id="again")

    def test_transitive_graph_dependencies_but_not_links_prerequisites_results(self):
        self.register("s")
        self.register("other")
        data = self.read()
        data.update(semantic_ref="semantic.json", tasks_ref="tasks.json")
        (self.run / "semantic.json").write_text(json.dumps({"contract_version":"0.1","run_id":"synthetic","nodes":[
            {"id":"n","revision":1,"kind":"claim","text":"Qualified synthetic claim", "uses":[{"id":"s","revision":1}],
             "links":[{"type":"supports","target":{"id":"other","revision":1}}]}]}), encoding="utf-8")
        tasks=[{"id":"t","revision":1,"objective":"fixture", "completion":"fixture saved","status":"completed",
                "input_refs":[{"id":"n","revision":1}],"prerequisites":[{"id":"p","revision":1}],"result_refs":[{"id":"other","revision":1}]},
               {"id":"p","revision":1,"objective":"prior", "completion":"done","status":"completed","input_refs":[],"prerequisites":[],"result_refs":[]}]
        (self.run / "tasks.json").write_text(json.dumps({"contract_version":"0.1","run_id":"synthetic","tasks":tasks}), encoding="utf-8")
        self.write(data)
        self.register("a",kind="artifact",uses=[("t",1)])
        for identity in ("s","n","t","a"):
            self.choose(identity)
        self.check()
        self.assertEqual(self.accept()["artifacts"][0]["acceptance_status"], "current")
        self.register("s",2)
        self.assertEqual(self.choose("s",2)["artifacts"][0]["acceptance_status"], "stale")

    def test_unselected_dependencies_block_acceptance(self):
        self.register("s")
        self.register("a",kind="artifact",uses=[("s",1)])
        self.choose("a")
        self.check()
        with self.assertRaisesRegex(ValueError,"pending"):
            self.accept()

    def test_wrong_target_or_missing_checks_and_source_acceptance_fail(self):
        self.register("a",kind="artifact")
        self.choose("a")
        with self.assertRaisesRegex(ValueError,"all registered checks"):
            self.accept()
        self.register("s")
        self.choose("s")
        self.check(identity="s")
        with self.assertRaisesRegex(ValueError,"Artifact"):
            self.accept(identity="s")
        self.check(check_id="c2")
        with self.assertRaisesRegex(ValueError,"exact target"):
            self.accept(check_ids=["c1"])

    def test_duplicate_cross_kind_invalid_revision_and_uses_refuse_without_record_change(self):
        self.register("s")
        before=(self.run/"run.json").read_bytes()
        for kwargs in [dict(identity="s",revision=1,kind="source"),dict(identity="s",revision=2,kind="artifact"),
                       dict(identity="new",revision=True,kind="source"),dict(identity="new",revision=0,kind="source"),
                       dict(identity="new",revision=1,kind="source",uses=[("absent",1)])]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.mutate("register",file=self.file,**kwargs)
            self.assertEqual((self.run/"run.json").read_bytes(),before)

    def test_artifact_requires_explicit_dependency_choice(self):
        with self.assertRaisesRegex(ValueError,"explicit"):
            self.mutate("register",identity="a",revision=1,kind="artifact",file=self.file)
        self.assertFalse((self.run/"versions").exists())

    def test_unknown_selection_and_same_choice_refused(self):
        with self.assertRaisesRegex(ValueError,"existing exact"):
            self.choose("none")
        self.register("s")
        self.choose("s")
        with self.assertRaisesRegex(ValueError,"already selected"):
            self.choose("s")

    def test_stale_expected_hash_and_existing_lock_preserve_everything(self):
        before=(self.run/"run.json").read_bytes()
        with self.assertRaisesRegex(ValueError,"stale expected"):
            self.helper.mutate(self.run,"0"*64,"select",reason="test",target=("s",1))
        self.assertFalse((self.run/self.helper.LOCK).exists())
        lock=self.run/self.helper.LOCK
        lock.write_bytes(b"another writer")
        with self.assertRaises(OSError):
            self.register("s")
        self.assertEqual(lock.read_bytes(),b"another writer")
        self.assertEqual((self.run/"run.json").read_bytes(),before)

    def test_atomic_replace_failure_preserves_old_record_and_orphan_history(self):
        before=(self.run/"run.json").read_bytes()
        with patch.object(self.helper.os,"replace",side_effect=OSError("synthetic write failure")):
            with self.assertRaisesRegex(ValueError,"no state commit"):
                self.register("s")
        self.assertEqual((self.run/"run.json").read_bytes(),before)
        self.assertEqual(len(list((self.run/"versions/history").glob("*.json"))),1)
        self.assertEqual(len(list((self.run/"versions/files").iterdir())),1)
        self.assertFalse((self.run/self.helper.LOCK).exists())
        self.assertFalse(list(self.run.glob(".run-*.tmp")))
        self.assertTrue(self.register("s")["valid"])

    def test_observed_file_race_refuses_commit(self):
        original=self.helper.exclusive
        before=(self.run/"run.json").read_bytes()
        def racing(path,data):
            original(path,data)
            if path.suffix==".tmp":
                self.file.write_bytes(b"changed concurrently")
        with patch.object(self.helper,"exclusive",side_effect=racing):
            with self.assertRaisesRegex(ValueError,"observed file changed"):
                self.register("s")
        self.assertEqual((self.run/"run.json").read_bytes(),before)

    def test_managed_write_reparse_component_refused(self):
        (self.run/"versions").mkdir()
        original=Path.lstat
        target=self.run/"versions"
        class Fake:
            st_mode=0o40755
            st_file_attributes=0x400
        def lstat(path,*args,**kwargs):
            return Fake() if path==target else original(path,*args,**kwargs)
        before=(self.run/"run.json").read_bytes()
        with patch.object(Path,"lstat",lstat):
            with self.assertRaisesRegex(ValueError,"reparse"):
                self.register("s")
        self.assertEqual((self.run/"run.json").read_bytes(),before)

    def test_package_mutation_refused(self):
        destination=self.package/"work"
        shutil.copytree(self.run,destination)
        with self.assertRaisesRegex(ValueError,"outside the installed"):
            self.helper.mutate(destination,self.digest(),"select",reason="test",target=("x",1))

    def test_malformed_extension_fails_closed(self):
        base=self.read()
        for bad in (None, [], {}, {"version":"0.1","selections":[{}],"acceptances":[]},
                    {"version":"0.1","selections":[],"acceptances":[{}]}):
            with self.subTest(bad=bad):
                data=deepcopy(base);data["version_state"]=bad;self.write(data)
                result=self.helper.inspect(self.run)
                self.assertTrue(result["structure_valid"])
                self.assertFalse(result["lifecycle_valid"])
                self.assertFalse(result["valid"])

    def test_remote_evidence_is_not_accepted(self):
        data=self.read()
        data["sources"]=[{"id":"s","revision":1,"ref":"https://example.invalid/input"}]
        self.write(data)
        self.register("a",kind="artifact",uses=[("s",1)])
        self.choose("s");self.choose("a");self.check()
        with self.assertRaisesRegex(ValueError,"local evidence"):
            self.accept()

    def test_inspection_is_read_only_and_input_script_never_runs(self):
        marker=self.root/"executed"
        self.file.write_text(f"from pathlib import Path\nPath({str(marker)!r}).touch()",encoding="utf-8")
        self.accepted()
        before={p.relative_to(self.run).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in self.run.rglob("*") if p.is_file()}
        self.helper.inspect(self.run)
        after={p.relative_to(self.run).as_posix():(p.read_bytes(),p.stat().st_mtime_ns) for p in self.run.rglob("*") if p.is_file()}
        self.assertEqual(before,after)
        self.assertFalse(marker.exists())

    def test_malformed_base_fields_return_invalid_without_body_or_traceback(self):
        for field in ("mode", "run_id", "work_status"):
            for value in (["PRIVATE_BODY_SENTINEL"], {"body":"PRIVATE_BODY_SENTINEL"}):
                with self.subTest(field=field,value=value):
                    data=deepcopy(self.record);data[field]=value;self.write(data)
                    result=self.helper.inspect(self.run)
                    self.assertFalse(result["valid"])
                    self.assertIsNone(result[field])
                    self.assertNotIn("PRIVATE_BODY_SENTINEL",json.dumps(result))
        process=subprocess.run([sys.executable,"-I",str(self.package/"scripts/report_versions.py"),"inspect",str(self.run)],
                               cwd=self.root,capture_output=True,text=True,encoding="utf-8")
        self.assertEqual(process.returncode,1,process.stdout+process.stderr)
        self.assertNotIn("Traceback",process.stderr)

    def test_changed_local_evidence_stales_even_after_manual_hash_refresh(self):
        self.accepted()
        data=self.read()
        source=data["sources"][0]
        (self.run/source["ref"]).write_bytes(b"changed source")
        result=self.helper.inspect(self.run)
        self.assertFalse(result["structure_valid"])
        source["content_hash"]=hashlib.sha256(b"changed source").hexdigest()
        self.write(data)
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"],"stale")
        with self.assertRaisesRegex(ValueError,"fresh actual Check"):
            self.accept(acceptance_id="again")

    def test_semantic_cycle_is_bounded_and_stale_evidence_blocks_acceptance(self):
        self.register("s")
        data=self.read();data["semantic_ref"]="semantic.json"
        nodes=[{"id":"n1","revision":1,"kind":"claim","text":"synthetic","status":"proposed",
                "uses":[{"id":"n2","revision":1}]},
               {"id":"n2","revision":1,"kind":"claim","text":"synthetic","status":"stale",
                "uses":[{"id":"n1","revision":1}]}]
        path=self.run/"semantic.json"
        path.write_text(json.dumps({"contract_version":"0.1","run_id":"synthetic","nodes":nodes}),encoding="utf-8")
        self.write(data)
        self.register("a",kind="artifact",uses=[("n1",1)])
        for identity in ("n1","n2","a"):self.choose(identity)
        self.check()
        result=self.helper.inspect(self.run)
        self.assertTrue(result["valid"])
        self.assertEqual(result["artifacts"][0]["currentness"]["state"],"pending")
        with self.assertRaisesRegex(ValueError,"pending"):self.accept()

    def test_failed_task_input_blocks_acceptance(self):
        data=self.read();data["tasks_ref"]="tasks.json"
        task={"id":"t","revision":1,"objective":"fixture","completion":"saved","status":"failed",
              "input_refs":[],"prerequisites":[],"result_refs":[]}
        (self.run/"tasks.json").write_text(json.dumps({"contract_version":"0.1","run_id":"synthetic","tasks":[task]}),encoding="utf-8")
        self.write(data)
        self.register("a",kind="artifact",uses=[("t",1)])
        self.choose("t");self.choose("a");self.check()
        with self.assertRaisesRegex(ValueError,"pending"):self.accept()

    def test_partial_snapshot_write_failure_preserves_record_and_releases_lock(self):
        before=(self.run/"run.json").read_bytes()
        original=self.helper.exclusive
        def fail_snapshot(path,data):
            if path.parent.name=="files":
                with path.open("xb") as stream:stream.write(data[:3])
                raise OSError("partial snapshot write")
            original(path,data)
        with patch.object(self.helper,"exclusive",side_effect=fail_snapshot):
            with self.assertRaisesRegex(ValueError,"no state commit"):self.register("s")
        self.assertEqual((self.run/"run.json").read_bytes(),before)
        self.assertEqual([p.read_bytes() for p in (self.run/"versions/files").iterdir()],[self.file.read_bytes()[:3]])
        self.assertFalse((self.run/self.helper.LOCK).exists())

    def verified_fixture(self):
        data=self.read();data["semantic_ref"]="semantic.json"
        node={"id":"claim","revision":1,"kind":"claim","text":"synthetic verified claim",
              "status":"verified","verification_refs":["claim-check"]}
        (self.run/"semantic.json").write_text(json.dumps({"contract_version":"0.1","run_id":"synthetic","nodes":[node]}),encoding="utf-8")
        (self.run/"claim-check.md").write_text("Synthetic claim verification fixture",encoding="utf-8")
        data["checks"].append({"id":"claim-check","target":{"id":"claim","revision":1},"status":"pass",
                               "detail_ref":"claim-check.md","method":"fixture method","scope":"claim scope"})
        self.write(data)
        self.register("a",kind="artifact",uses=[("claim",1)])
        self.choose("claim");self.choose("a");self.check();self.accept()

    def test_explicit_verification_check_detail_change_stales_acceptance(self):
        self.verified_fixture()
        (self.run/"claim-check.md").write_text("Changed claim verification",encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"],"stale")
        with self.assertRaisesRegex(ValueError,"fresh actual Check"):
            self.accept(acceptance_id="again")

    def test_unreferenced_check_details_do_not_stale_acceptance(self):
        self.verified_fixture()
        self.register("unrelated")
        self.check(identity="unrelated",check_id="unrelated-check")
        (self.run/"unrelated-check.md").write_text("Changed unrelated review",encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"],"current")

    def test_conflict_disposition_details_are_bound_to_new_acceptance(self):
        self.verified_fixture()
        self.check(identity="claim", check_id="conflict", status="fail")
        path = self.run / "semantic.json"
        semantic = json.loads(path.read_text(encoding="utf-8"))
        semantic["nodes"][0]["verification_dispositions"] = [{"check_id":"conflict", "disposition":"resolved",
            "reason":"Synthetic reconsideration", "detail_ref":"resolution.md", "resolving_check_id":"claim-check"}]
        (self.run / "resolution.md").write_text("Synthetic resolution review", encoding="utf-8")
        path.write_text(json.dumps(semantic), encoding="utf-8")
        self.check(check_id="new-check")
        self.accept(acceptance_id="resolved-acceptance", check_ids=["new-check"])
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "current")
        (self.run / "resolution.md").write_text("Changed resolution scope", encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")

    def test_nested_managed_package_is_refused_before_lock_or_snapshot(self):
        for relative in ("versions", "versions/files", "versions/history"):
            for marker in ("SKILL.md", "bundle-manifest.json"):
                with self.subTest(relative=relative, marker=marker):
                    protected = self.run / relative
                    protected.mkdir(parents=True, exist_ok=True)
                    marker_path = protected / marker
                    marker_path.write_bytes(b"recognized unrelated Skill")
                    before = {p.relative_to(self.run): (p.read_bytes(), p.stat().st_mtime_ns)
                              for p in self.run.rglob("*") if p.is_file()}
                    with self.assertRaisesRegex(ValueError, "installed Skill"):
                        self.register("s")
                    self.assertFalse((self.run / self.helper.LOCK).exists())
                    self.assertEqual(before, {p.relative_to(self.run): (p.read_bytes(), p.stat().st_mtime_ns)
                                             for p in self.run.rglob("*") if p.is_file()})
                    marker_path.unlink()

    def test_cross_package_mutation_refuses_before_lock_or_history(self):
        (self.root / "SKILL.md").write_text("another installed package", encoding="utf-8")
        before = {str(p.relative_to(self.run)): p.read_bytes() for p in self.run.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(ValueError, "outside.*Skill"):
            self.register("s")
        self.assertEqual(before, {str(p.relative_to(self.run)): p.read_bytes() for p in self.run.rglob("*") if p.is_file()})

    def test_decision_context_progress_log_and_scope_revision(self):
        self.register("context")
        self.choose("context")
        self.mutate("set-context", target=("context", 1))
        self.register("a", kind="artifact")
        self.choose("a")
        self.check()
        self.accept()
        self.assertEqual(self.read()["version_state"]["acceptances"][0]["context_mode"], "decision_context_v1")
        (self.run / "run.md").write_text("Progress only: render began", encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "current")
        self.file.write_text("Changed communication objective", encoding="utf-8")
        self.register("context", 2)
        self.choose("context", 2)
        self.mutate("set-context", target=("context", 2))
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")
        with self.assertRaisesRegex(ValueError, "fresh actual Check"):
            self.accept(acceptance_id="again")

    def test_legacy_acceptance_keeps_legacy_notes_rule_after_context_binding(self):
        self.accepted()
        self.register("context")
        self.choose("context")
        self.mutate("set-context", target=("context", 1))
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "current")
        (self.run / "run.md").write_text("Legacy notes still bound", encoding="utf-8")
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")

    def test_context_requires_selected_hashed_source_and_no_noop(self):
        self.register("context")
        with self.assertRaisesRegex(ValueError, "select"):
            self.mutate("set-context", target=("context", 1))
        self.choose("context")
        self.mutate("set-context", target=("context", 1))
        with self.assertRaisesRegex(ValueError, "already bound"):
            self.mutate("set-context", target=("context", 1))
        self.register("a", kind="artifact")
        with self.assertRaisesRegex(ValueError, "Source"):
            self.mutate("set-context", target=("a", 1))

    def test_context_cli_and_missing_bound_context_invalidates_new_acceptance(self):
        self.register("context"); self.choose("context")
        process = subprocess.run([sys.executable, "-I", str(self.package / "scripts/report_versions.py"),
            "set-context", str(self.run), "--target", "context@1", "--reason", "explicit decision scope",
            "--expect-run-sha256", self.digest()], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(process.returncode, 0, process.stderr + process.stdout)
        self.register("a", kind="artifact"); self.choose("a"); self.check(); self.accept()
        data = self.read(); data.pop("decision_context"); self.write(data)
        self.assertEqual(self.helper.inspect(self.run)["artifacts"][0]["acceptance_status"], "stale")

    def test_standalone_isolated_cli_and_report_inspect_integration(self):
        self.accepted()
        cwd=self.root/"unrelated";cwd.mkdir()
        self.assertFalse(list(self.package.rglob("__pycache__")))
        for script in ("report_versions.py","report_run.py"):
            process=subprocess.run([sys.executable,"-I",str(self.package/"scripts"/script),"inspect",str(self.run)],
                                   cwd=cwd,capture_output=True,text=True,encoding="utf-8")
            self.assertEqual(process.returncode,0,process.stderr+process.stdout)
            result=json.loads(process.stdout)
            if script=="report_run.py":result=result["version_lifecycle"]
            self.assertEqual(result["artifacts"][0]["acceptance_status"],"current")
        self.assertFalse(list(self.package.rglob("__pycache__")))


if __name__ == "__main__":
    unittest.main()
