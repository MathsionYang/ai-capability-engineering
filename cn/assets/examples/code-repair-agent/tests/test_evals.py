import tempfile
import unittest
from collections import Counter
from pathlib import Path

import yaml

RUNNER_DIR = Path(__file__).parents[1]
import sys
sys.path.insert(0, str(RUNNER_DIR))

from run_evals import run_cases  # noqa: E402


CASES_PATH = RUNNER_DIR / "eval_cases.yaml"
REQUIRED = {"case_id", "category", "scenario", "input", "expected", "forbidden_actions", "required_evidence", "artifacts", "rubric", "fixtures"}
EXPECTED_COUNTS = {"normal": 10, "input_incomplete": 5, "tool_failure": 5, "high_risk": 5, "historical_regression": 5}


class EvalContractTest(unittest.TestCase):
    def test_golden_set_has_exact_categories_and_fields(self):
        cases = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(cases), 30)
        self.assertEqual(Counter(case["category"] for case in cases), EXPECTED_COUNTS)
        for case in cases:
            self.assertTrue(REQUIRED.issubset(case))
            self.assertTrue(case["fixtures"].get("tools"))
            self.assertTrue(case["fixtures"].get("model"))
            self.assertTrue(case["rubric"])
            for artifact in case["artifacts"] + case["input"].get("artifacts", []):
                self.assertTrue(artifact["ref"].startswith("artifact://"))
                self.assertRegex(artifact["hash"], r"^sha256:[0-9a-f]{64}$")

    def test_batch_runner_reports_gate_and_stable_results(self):
        with tempfile.TemporaryDirectory() as temp:
            first = run_cases(CASES_PATH, Path(temp) / "first")
            second = run_cases(CASES_PATH, Path(temp) / "second")
            self.assertEqual(first["total"], 30)
            self.assertEqual(first["category_counts"], EXPECTED_COUNTS)
            self.assertEqual(first["pass_rate"], 1.0)
            self.assertEqual(first["release_decision"], "blocked")
            self.assertTrue((Path(temp) / "first" / "regression-report.md").exists())
            self.assertIn("Failure Attribution", (Path(temp) / "first" / "regression-report.md").read_text(encoding="utf-8"))
            self.assertEqual(first["failure_classes"], second["failure_classes"])
            self.assertEqual(first["category_counts"], second["category_counts"])
            self.assertTrue(all(item["trace_path"] for item in first["cases"]))
            high_risk = [item for item in first["cases"] if item["category"] == "high_risk"]
            self.assertEqual(len(high_risk), 5)
            self.assertTrue(all(item["decision"] in {"blocked", "human-review"} for item in high_risk))

    def test_baseline_regression_blocks_release(self):
        with tempfile.TemporaryDirectory() as temp:
            report = run_cases(CASES_PATH, Path(temp), baseline_success_rate=1.1)
            self.assertEqual(report["release_decision"], "blocked")
            self.assertIn("success_rate_regression", report["gate_reasons"])


if __name__ == "__main__":
    unittest.main()
