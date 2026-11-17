"""Normal export and real browser search must expose the registered design recipes."""
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skill-src/how-to-report/scripts"))

from presentation_storybook import _builtin_records, build_storybook
from report_ppt import DEFAULT_TEMPLATE


@unittest.skipUnless(importlib.util.find_spec("playwright"), "Playwright is required for actual browser search")
class StorybookSearchTests(unittest.TestCase):
    def test_exported_design_role_is_searchable_and_opens_matching_recipe_requests(self):
        from playwright.sync_api import expect, sync_playwright
        expected = {"editorial-pillars", "stage-ribbon", "capability-platform"}
        records = list(_builtin_records(DEFAULT_TEMPLATE))
        self.assertEqual(sum(r.get("presentation_role") == "designed-composition" for r in records), 3)
        self.assertEqual(sum(r.get("presentation_role") == "structural-template" for r in records), 170)
        self.assertTrue(any(r["kind"] == "icon" for r in records))
        self.assertTrue(any(r["kind"] == "chart" for r in records))
        with tempfile.TemporaryDirectory(prefix="storybook-search-") as temporary:
            output = Path(temporary) / "site"
            build_storybook(None, output, include_builtin=False, extra_records=records)
            with sync_playwright() as runtime:
                if not Path(runtime.chromium.executable_path).is_file():
                    self.skipTest("Playwright Chromium is not installed")
                browser = runtime.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.goto((output / "index.html").as_uri(), wait_until="networkidle")
                    page.locator("#search").fill("DESIGNED-COMPOSITION")
                    expect(page.locator("#results")).to_have_text(re.compile(r"^找到 3 项"))
                    self.assertEqual(page.locator("#cards article.card").count(), 3)
                    found = set()
                    for index in range(3):
                        page.locator("#cards article.card").nth(index).get_by_role("button", name="查看详情").click()
                        page.locator("#detail").wait_for(state="visible")
                        request = json.loads(page.locator("#request").input_value())
                        self.assertEqual(len(request["pages"]), 1)
                        found.add(request["pages"][0]["recipe"])
                        page.locator("#close-detail").click()
                    self.assertEqual(found, expected)
                    page.locator("#search").fill("structural-template")
                    expect(page.locator("#results")).to_have_text(re.compile(r"^找到 170 项"))
                    self.assertEqual(page.locator("#cards article.card").count(), 24)
                    # The narrow index must retain useful selection guidance too.
                    selected = next(r for r in records if r.get("presentation_role") == "designed-composition")
                    guidance = selected["selection_guidance"].split("；")[0]
                    page.locator("#search").fill(guidance)
                    expect(page.locator("#results")).to_have_text(re.compile(r"^找到 3 项"))
                    page.locator("#search").fill("结构基础候选")
                    expect(page.locator("#results")).to_have_text(re.compile(r"^找到 170 项"))
                    page.locator("#search").fill("no-such-design-role-0116")
                    expect(page.locator("#results")).to_have_text(re.compile(r"^找到 0 项"))
                    self.assertEqual(page.locator("#cards article.card").count(), 0)
                finally:
                    browser.close()


if __name__ == "__main__":
    unittest.main()
