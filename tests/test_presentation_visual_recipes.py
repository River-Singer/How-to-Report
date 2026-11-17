"""Visual design recipes retain measured replay, discoverability and global colour roles."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skill-src/how-to-report"
sys.path.insert(0, str(SOURCE / "scripts"))
from report_ppt import read_json
from presentation_recipes import compose_document
from presentation_compiler import build_project
from presentation_library import library, profile_path
from presentation_palette import apply_palette, describe_palette, label_ink, contrast_ratio


class VisualRecipeTests(unittest.TestCase):
    def setUp(self):
        self.request = read_json(SOURCE / "assets/design-system/examples/presentation-ui.json")

    def test_global_spectrum_keeps_type_and_geometry_and_readable_labels(self):
        tokens = read_json(profile_path())
        changed = apply_palette(tokens, "consulting-spectrum")
        for key in tokens.keys() - {"color", "theme"}:
            self.assertEqual(changed[key], tokens[key])
        self.assertEqual(apply_palette(tokens, "report-default"), tokens)
        palette = describe_palette("consulting-spectrum")
        self.assertEqual(palette["roles"]["body"], "#333333")
        self.assertEqual(palette["roles"]["muted"], "#A6A6A6")
        self.assertEqual(len(palette["categorical"]), 6)
        for color in palette["categorical"]:
            self.assertGreaterEqual(contrast_ratio(label_ink(color), color), 4.5)
        self.assertEqual(changed["theme"]["slots"]["accent1"], palette["roles"]["primary"])
        self.assertEqual(changed["color"]["palette"]["categorical"], palette["categorical"])

    def test_registered_designed_candidates_have_own_example_and_real_preview(self):
        for name in ("editorial-pillars", "stage-ribbon", "capability-platform"):
            record = library(identifier="recipe." + name)
            self.assertEqual(record["presentation_role"], "designed-composition")
            self.assertEqual(record["example"]["project_id"], self.request["project_id"])
            self.assertTrue(record["executable"])
            for preview in record["preview_refs"]:
                self.assertTrue((SOURCE / preview["ref"]).is_file(), preview)
        result = library(kind="template", limit=1)
        self.assertEqual(result["items"][0]["presentation_role"], "structural-template")

    def test_native_build_replays_source_after_fact_and_item_change(self):
        import ppt_runtime
        author = compose_document(self.request)
        self.assertTrue(all(page.get("recipe_source") for page in author["pages"]))
        with tempfile.TemporaryDirectory(prefix="visual-recipe-replay-") as directory:
            before, after = Path(directory) / "before", Path(directory) / "after"
            build_project(author, before, geometry_policy="computed")
            first = read_json(before / "layout/03_capability-platform.scene.json")["scene"]
            # Cached frames are deliberately corrupt: computed replay must ignore them.
            for page in author["pages"]:
                page["elements"] = [{"id":page["id"] + "-stale", "type":"shape", "shape":"rect", "frame":[9000,9000,2,2]}]
            author["facts"]["shared-copy"]["value"] = "统一业务对象与专业规则，保留需求、数据、结论之间的对应关系。\n记录权限、版本和修改原因，让评估与执行使用相同的信息。\n将核验过的记录提供给评估、执行和复盘，保留来源与适用边界。"
            author["pages"][0]["recipe_source"]["slots"]["items"].append({"title":"知识复用", "body":"保存有效做法\n注明适用条件\n形成共享经验"})
            build_project(author, after, geometry_policy="computed")
            second = read_json(after / "layout/03_capability-platform.scene.json")["scene"]
            target = "capability-platform--ui-platform--surface"
            old_box = next(e["frame"] for e in first["elements"] if e["id"] == target)
            new_box = next(e["frame"] for e in second["elements"] if e["id"] == target)
            self.assertGreater(new_box[3], old_box[3])
            rebuilt = read_json(after / "layout/01_editorial-pillars.scene.json")["scene"]
            self.assertTrue(any(e["id"].endswith("pillar-title-3-label") for e in rebuilt["elements"]))
            self.assertFalse(any(e["id"].endswith("-stale") for e in rebuilt["elements"]))
            branches = [e for e in second["elements"] if e["type"] == "connector" and "-branch-" in e["id"]]
            self.assertEqual(len(branches), 5)
            self.assertEqual(sum(e["from"].startswith("capability-platform--ui-inputs-") and e["from"].endswith("--surface") for e in branches), 3)
            self.assertEqual(sum(e["to"].startswith("capability-platform--ui-outputs-") and e["to"].endswith("--surface") for e in branches), 2)
            report = read_json(after / "layout/03_capability-platform.report.json")
            self.assertEqual(report["geometry_policy"], "computed")
            self.assertIn("presentation_visual_recipes.py", report["compiler_files"])
            self.assertEqual(ppt_runtime.check_project(after)["status"], "pass")
            self.assertEqual(ppt_runtime.export_project(after, Path(directory) / "replayed.pptx", after / "tokens.json")["status"], "pass")

    def test_contract_rejects_geometry_overrides_overcapacity_and_overflow(self):
        for mutation in ("frame", "font", "capacity", "overflow"):
            request = deepcopy(self.request)
            request["pages"] = [request["pages"][0]]
            slots = request["pages"][0]["slots"]
            if mutation == "frame": slots["items"][0]["frame"] = [0, 0, 100, 100]
            elif mutation == "font": slots["items"][0]["font_size"] = 6
            elif mutation == "capacity": slots["items"] *= 2
            else: slots["items"][0]["body"] = "实际容量溢出必须显式调整内容与分组，不能缩字。" * 160
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                compose_document(request)

    def test_corrected_resource_index_keeps_values_without_fake_comparison(self):
        document = read_json(ROOT / "examples/consulting-explanatory/authors/metric-evidence-columns.json")
        quantities = [fact["value"] for key, fact in document["facts"].items() if ".quantity-" in key]
        self.assertEqual(quantities, ["200", "12", "80", "4", "3"])
        import json
        self.assertNotIn('"chart.column"', json.dumps(document))
        with tempfile.TemporaryDirectory(prefix="resource-lookup-") as directory:
            build_project(document, Path(directory) / "build", geometry_policy="computed")


if __name__ == "__main__":
    unittest.main()
