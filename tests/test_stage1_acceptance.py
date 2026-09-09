import re
import unittest
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
CHECKLIST = next(path for path in ROOT.rglob("*Checklist*") if path.is_file())
ARTICLE = next(path for path in ROOT.rglob("*.md") if path.parent.name != "assets" and "Agent" in path.name and "Trace" in path.name and "Evals" in path.name)
CASES = ROOT / "cn" / "assets" / "examples" / "code-repair-agent" / "eval_cases.yaml"


class Stage1AcceptanceTest(unittest.TestCase):
    def test_stage1_checklist_is_checked_but_stage2_and_stage3_are_not(self):
        lines = CHECKLIST.read_text(encoding="utf-8").splitlines()
        stage1 = "\n".join(lines[101:180])
        stage2 = "\n".join(lines[180:247])
        stage3 = "\n".join(lines[247:])
        self.assertGreaterEqual(len(re.findall(r"- \[x\]", stage1)), 10)
        self.assertNotIn("- [x]", stage2)
        self.assertNotIn("- [x]", stage3)

    def test_stage1_trace_field_extraction_is_checked(self):
        lines = CHECKLIST.read_text(encoding="utf-8").splitlines()
        targets = [line for line in lines if line.startswith("- [") and "Trace" in line and "字段" in line]
        self.assertEqual(len(targets), 1)
        self.assertTrue(targets[0].startswith("- [x]"))

    def test_stage1_assets_and_navigation_targets_exist(self):
        for path in (
            ARTICLE,
            ROOT / "cn" / "assets" / "schemas" / "trace-event.md",
            ROOT / "cn" / "assets" / "schemas" / "checkpoint-state.yaml",
            ROOT / "cn" / "assets" / "schemas" / "eval-case.yaml",
            ROOT / "cn" / "assets" / "checklists" / "validator-decision.md",
            ROOT / "cn" / "assets" / "checklists" / "regression-report.md",
            ROOT / "cn" / "assets" / "examples" / "code-repair-agent" / "runner.py",
            ROOT / "cn" / "assets" / "examples" / "code-repair-agent" / "run_evals.py",
        ):
            self.assertTrue(path.exists(), path)
        self.assertIn("Trace", (ROOT / "cn" / "index.md").read_text(encoding="utf-8"))
        self.assertIn("Trace", (ROOT / "Readme.md").read_text(encoding="utf-8"))
        self.assertIn("Stage 1 trusted execution", (ROOT / "mkdocs.yml").read_text(encoding="utf-8"))

    def test_eval_distribution_is_exact(self):
        cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 30)
        self.assertEqual(Counter(case["category"] for case in cases), {"normal": 10, "input_incomplete": 5, "tool_failure": 5, "high_risk": 5, "historical_regression": 5})


if __name__ == "__main__":
    unittest.main()
