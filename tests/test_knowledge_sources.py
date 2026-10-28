"""Network-free archive integrity, scope mapping and extraction regressions."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vendor_knowledge_sources", PROJECT / "tools/vendor_knowledge_sources.py")
vendor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vendor)


class OfflineSourcesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "sources").mkdir()
        text = b"Synthetic local reference text.\n"
        (self.root / "sources/example.txt").write_bytes(text)
        (self.root / "card.md").write_text("[Reference](sources/example.txt)\n", encoding="utf-8")
        self.data = {
            "schema_version": "1", "runtime_network_required": False,
            "card_sources": {"card.md": ["example"]},
            "sources": [{"id": "example", "title": "Example", "publisher": "Synthetic test",
                         "canonical_url": "https://example.com/reference", "local_path": "sources/example.txt",
                         "fetched_at_utc": "2026-10-26T00:00:00+00:00", "scope": "Synthetic test text",
                         "representation": "source_text", "card_ids": ["TEST-01"],
                         "retrieval": {"method": "https_html_body"},
                         "reuse": {"license": "Synthetic", "evidence_url": "https://example.com/license",
                                   "attribution": "Test author", "limitations": "Synthetic fixture only"},
                         "sha256": hashlib.sha256(text).hexdigest()}],
        }
        self.save()

    def save(self):
        (self.root / "sources/manifest.json").write_text(json.dumps(self.data), encoding="utf-8")

    def test_shipped_archive_checks_with_network_forbidden(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network forbidden")), patch.object(
            vendor.urllib.request, "urlopen", side_effect=AssertionError("network forbidden")
        ):
            self.assertEqual(vendor.check(PROJECT / "skill-src/shared/knowledge"), [])

    def test_corrupted_source_is_detected(self):
        (self.root / "sources/example.txt").write_text("tampered", encoding="utf-8")
        self.assertTrue(any("hash mismatch" in error for error in vendor.check(self.root)))

    def test_missing_and_unregistered_text_are_detected(self):
        (self.root / "sources/example.txt").unlink()
        (self.root / "sources/unregistered.txt").write_text("unexpected", encoding="utf-8")
        errors = vendor.check(self.root)
        self.assertTrue(any("inventory mismatch" in error for error in errors))

    def test_card_cannot_silently_drop_required_source_or_add_network_link(self):
        (self.root / "card.md").write_text("[Remote](https://example.com/reference)\n", encoding="utf-8")
        errors = vendor.check(self.root)
        self.assertTrue(any("mapping mismatch" in error for error in errors))
        self.assertTrue(any("external body link" in error for error in errors))

    def test_archive_path_escape_is_rejected(self):
        self.data["sources"][0]["local_path"] = "../outside.txt"
        self.save()
        self.assertTrue(any("unsafe source path" in error for error in vendor.check(self.root)))

    def test_bad_metadata_and_duplicate_identity_are_rejected(self):
        self.data["sources"].append(dict(self.data["sources"][0]))
        self.save()
        self.assertTrue(any("duplicate" in error for error in vendor.check(self.root)))
        self.data["sources"] = ["not an object"]
        self.save()
        self.assertTrue(any("must be an object" in error for error in vendor.check(self.root)))

    def test_summary_cannot_be_refetched_as_approved_full_source(self):
        source = self.data["sources"][0]
        source["representation"] = "original_summary"
        with patch.object(vendor.urllib.request, "urlopen", side_effect=AssertionError("must not fetch")):
            with self.assertRaises(vendor.SourceError):
                vendor.fetch_candidate(source)

    def test_fetch_rejects_existing_and_archive_outputs_before_network(self):
        with tempfile.TemporaryDirectory() as destination:
            existing = Path(destination) / "existing.txt"
            existing.write_text("preserve", encoding="utf-8")
            archive_candidate = self.root / "sources/new.txt"
            missing_canonical = self.root / "sources/example.txt"
            missing_canonical.unlink()
            with patch.object(vendor, "fetch_candidate", side_effect=AssertionError("must not fetch")), redirect_stderr(io.StringIO()):
                for output in (existing, archive_candidate, missing_canonical):
                    self.assertEqual(vendor.main(["fetch", "--root", str(self.root), "--source-id", "example", "--output", str(output)]), 1)
            self.assertEqual(existing.read_text(encoding="utf-8"), "preserve")
            self.assertFalse(archive_candidate.exists())
            self.assertFalse(missing_canonical.exists())

    def test_fetch_writes_new_review_candidate_without_archive_mutation(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        with tempfile.TemporaryDirectory() as destination:
            output = Path(destination) / "candidate.txt"
            with patch.object(vendor, "fetch_candidate", return_value=("new reviewed later body\n", {"resolved_url": "https://example.com/reference"})), redirect_stdout(io.StringIO()):
                self.assertEqual(vendor.main(["fetch", "--root", str(self.root), "--source-id", "example", "--output", str(output)]), 0)
            self.assertIn("new reviewed later body", output.read_text(encoding="utf-8"))
        after = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_fetch_requires_https_and_rejects_redirect_downgrade(self):
        source = self.data["sources"][0]
        with patch.object(vendor.urllib.request, "build_opener", side_effect=AssertionError("must not fetch")):
            for url in ("http://example.com/reference", "file:///local.html", "https:///missing-host", "https://user:secret@example.com/reference"):
                source["canonical_url"] = url
                with self.assertRaises(vendor.SourceError):
                    vendor.fetch_candidate(source)
        with self.assertRaises(vendor.SourceError):
            vendor.HttpsOnlyRedirectHandler().redirect_request(None, None, 302, "Found", {}, "http://example.com/reference")

    def test_network_contract_and_unreadable_card_report_errors(self):
        self.data["runtime_network_required"] = True
        self.save()
        self.assertTrue(any("runtime_network_required" in error for error in vendor.check(self.root)))
        self.data["runtime_network_required"] = False
        self.save()
        (self.root / "card.md").write_bytes(b"\xff")
        self.assertTrue(any("cannot read card" in error for error in vendor.check(self.root)))

    def test_extraction_preserves_body_and_excludes_scripts_and_navigation(self):
        html = "<body><nav>outside</nav><article id='main'><h1>Title</h1><p>" + "Evidence with conditions. " * 8 + "</p><script>evil()</script><nav>menu</nav></article></body>"
        text = vendor.extract_html(html, {"id": "main"})
        self.assertIn("Title", text)
        self.assertEqual(text.count("Evidence with conditions."), 8)
        self.assertNotIn("evil", text)
        self.assertNotIn("menu", text)
        self.assertNotIn("outside", text)

    def test_missing_or_ambiguous_body_requires_review(self):
        with self.assertRaises(vendor.SourceError):
            vendor.extract_html("<p>Not the body</p>", {"id": "main"})
        with self.assertRaises(vendor.SourceError):
            vendor.extract_html("<div id='main'>A</div><div id='main'>B</div>", {"id": "main"})


if __name__ == "__main__":
    unittest.main()
