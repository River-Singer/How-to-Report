"""Check suite entry resources and relocation, with no model or PPT execution."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "tools" / "package_skills.py"
SPEC = importlib.util.spec_from_file_location("suite_packager", SCRIPT)
assert SPEC and SPEC.loader
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class SuiteEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = (PROJECT / "SKILL.md").read_bytes()
        cls.packages = packager.expected_packages(PROJECT)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="report-suite-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.suite = self.base / "relocated suite"
        self.suite.mkdir()
        (self.suite / "SKILL.md").write_bytes(self.entry)
        for skill, payload in self.packages.items():
            self.write_payload(self.suite / "skills" / skill, payload)

    @staticmethod
    def write_payload(destination: Path, payload: dict[str, bytes]) -> None:
        for relative, content in payload.items():
            path = destination / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    def test_suite_frontmatter_identifies_the_complete_checkout_entry(self) -> None:
        entry = self.entry.decode("utf-8-sig")
        frontmatter = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", entry, re.DOTALL)
        self.assertIsNotNone(frontmatter)
        metadata = frontmatter.group(1)
        self.assertRegex(metadata, r"(?m)^name:[ \t]*how-to-report-suite[ \t]*\r?$")
        self.assertRegex(metadata, r"(?m)^description:[ \t]*\S.+$")

    def test_relocated_suite_reaches_both_skills_and_the_ppt_handoff(self) -> None:
        entry = (self.suite / "SKILL.md").read_text(encoding="utf-8-sig")
        targets = {
            packager.local_target("how-to-report-suite", "SKILL.md", link)
            for link in packager.markdown_links(entry)
        }
        targets.discard(None)
        self.assertIn("skills/how-to-report/SKILL.md", targets)
        self.assertIn("skills/report-audit/SKILL.md", targets)
        for target in targets:
            with self.subTest(target=target):
                self.assertTrue((self.suite / target).is_file(), target)

        generator = self.suite / "skills" / "how-to-report"
        generator_targets = {
            packager.local_target("how-to-report", "SKILL.md", link)
            for link in packager.markdown_links(
                (generator / "SKILL.md").read_text(encoding="utf-8-sig")
            )
        }
        self.assertIn("references/ppt-handoff.md", generator_targets)
        self.assertTrue((generator / "references" / "ppt-handoff.md").is_file())
        self.assertFalse((self.suite / "skill-src").exists())
        self.assertFalse((self.suite / "ppt-master").exists())

    def test_handoff_remains_package_local_without_external_or_sibling_installation(self) -> None:
        standalone = self.base / "standalone-how-to-report"
        self.write_payload(standalone, self.packages["how-to-report"])
        payload, _ = packager.tree(standalone)
        packager.validate_payload("how-to-report", payload)
        self.assertFalse((standalone.parent / "report-audit").exists())
        self.assertFalse((standalone.parent / "ppt-master").exists())

        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run(
            [sys.executable, str(standalone / "scripts" / "validate_run.py"), "--help"],
            cwd=self.base, env=environment, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        missing_handoff = dict(payload)
        missing_handoff.pop("references/ppt-handoff.md")
        with self.assertRaisesRegex(packager.PackageError, "ppt-handoff.md"):
            packager.validate_payload("how-to-report", missing_handoff)

    def test_challenge_selection_reaches_shared_method_and_evidence_rules(self) -> None:
        shared = PROJECT / "skill-src" / "shared" / "references"
        method_paths = (
            "references/directed-challenge.md",
            "references/agent-delegation.md",
            "references/stakeholder-roles.md",
        )
        for skill, payload in self.packages.items():
            with self.subTest(skill=skill):
                standalone = self.base / ("challenge-" + skill)
                self.write_payload(standalone, payload)
                relocated, _ = packager.tree(standalone)
                packager.validate_payload(skill, relocated)
                for relative in method_paths:
                    self.assertEqual(relocated[relative], (shared / Path(relative).name).read_bytes())
                for relative in method_paths[1:]:
                    targets = {
                        packager.local_target(skill, relative, link)
                        for link in packager.markdown_links(relocated[relative].decode("utf-8-sig"))
                    }
                    self.assertIn("references/directed-challenge.md", targets)
                evidence_targets = {
                    packager.local_target(skill, method_paths[0], link)
                    for link in packager.markdown_links(relocated[method_paths[0]].decode("utf-8-sig"))
                }
                self.assertIn("references/semantic-structuring.md", evidence_targets)


if __name__ == "__main__":
    unittest.main()
