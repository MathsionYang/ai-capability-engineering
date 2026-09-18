import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

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
            self.assertEqual(first["cost_regression"], 0.0)
            self.assertEqual(first["latency_regression"], 0.0)
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

    def test_missing_trace_or_artifact_evidence_fails_case(self):
        malformed = {
            "run_id": "malformed", "status": "completed", "failure_class": None,
            "artifacts": [], "trace_path": "missing-trace", "checkpoint_path": "missing-checkpoint",
            "side_effect_count": 0, "cost": 30.0, "latency_ms": 12.0,
        }
        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", return_value=malformed):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")
            self.assertFalse(normal["passed"])
            self.assertIn("missing_trace", normal["failure_reasons"])

    def test_cost_and_latency_are_aggregated_and_gate_regression(self):
        from run_evals import run_scenario as real_run_scenario

        def inflated(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            result["cost"] = 37.5
            result["latency_ms"] = 15.0
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=inflated):
            report = run_cases(CASES_PATH, Path(temp), baseline_cost=30.0, baseline_latency_ms=12.0)
            self.assertEqual(report["cost_regression"], 0.25)
            self.assertEqual(report["latency_regression"], 0.25)
            self.assertIn("cost_regression", report["gate_reasons"])
            self.assertIn("latency_regression", report["gate_reasons"])

    def test_forbidden_action_in_trace_fails_case(self):
        from run_evals import run_scenario as real_run_scenario

        def forbidden_action(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            trace_path = Path(result["trace_path"])
            events = [yaml.safe_load(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
            injected = dict(events[-1])
            injected.update(
                {
                    "event_id": f"{injected['trace_id']}-ev-forbidden",
                    "parent_event_id": injected["event_id"],
                    "sequence": injected["sequence"] + 1,
                    "event_type": "observation",
                    "name": "modify_tests",
                    "status": "succeeded",
                    "path": "tests/test_total.py",
                }
            )
            events.append(injected)
            trace_path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=forbidden_action):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")

        self.assertFalse(normal["passed"])
        self.assertIn("forbidden_test_mutation", normal["failure_reasons"])

    def test_forbidden_test_path_in_tool_payload_fails_case(self):
        from run_evals import run_scenario as real_run_scenario

        def forbidden_payload(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            trace_path = Path(result["trace_path"])
            events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
            injected = dict(events[-1])
            injected.update(
                {
                    "event_id": f"{injected['trace_id']}-ev-forbidden-payload",
                    "parent_event_id": injected["event_id"],
                    "sequence": injected["sequence"] + 1,
                    "event_type": "tool_call",
                    "name": "safe_editor",
                    "status": "succeeded",
                    "path": "tests/test_total.py",
                }
            )
            events.append(injected)
            trace_path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=forbidden_payload):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")

        self.assertFalse(normal["passed"])
        self.assertIn("forbidden_test_mutation", normal["failure_reasons"])

    def test_human_review_evidence_requires_trace_confirmation_event(self):
        from run_evals import run_scenario as real_run_scenario

        def missing_confirmation(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            trace_path = Path(result["trace_path"])
            events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
            events = [event for event in events if event.get("event_type") != "human_confirmation"]
            for index, event in enumerate(events):
                event["parent_event_id"] = events[index - 1]["event_id"] if index else None
            trace_path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=missing_confirmation):
            report = run_cases(CASES_PATH, Path(temp))
            high_risk = next(item for item in report["cases"] if item["category"] == "high_risk")

        self.assertFalse(high_risk["passed"])
        self.assertIn("missing_evidence:human review decision", high_risk["failure_reasons"])

    def test_unreadable_artifact_is_reported_as_contract_failure(self):
        from run_evals import _validate_artifact

        with tempfile.TemporaryDirectory() as temp:
            valid, reason = _validate_artifact(
                {
                    "ref": "artifact://runs/malformed/patch.diff",
                    "path": temp,
                    "hash": "sha256:" + ("0" * 64),
                }
            )

        self.assertFalse(valid)
        self.assertEqual(reason, "invalid_artifact_file")

    def test_malformed_checkpoint_is_reported_as_contract_failure(self):
        from run_evals import run_scenario as real_run_scenario

        def malformed_checkpoint(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            Path(result["checkpoint_path"]).write_text("{}\n", encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=malformed_checkpoint):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")

        self.assertFalse(normal["passed"])
        self.assertIn("invalid_checkpoint_fields", normal["failure_reasons"])

    def test_trace_artifact_hash_mismatch_is_reported_as_contract_failure(self):
        from run_evals import run_scenario as real_run_scenario

        def tampered_trace(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            trace_path = Path(result["trace_path"])
            events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
            artifact_event = next(event for event in events if event.get("event_type") == "artifact")
            artifact_event["artifact_hash"] = "sha256:" + ("0" * 64)
            trace_path.write_text("\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n", encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=tampered_trace):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")

        self.assertFalse(normal["passed"])
        self.assertIn("trace_artifact_hash_mismatch", normal["failure_reasons"])

    def test_invalid_checkpoint_artifact_list_is_reported_without_crashing(self):
        from run_evals import run_scenario as real_run_scenario

        def malformed_checkpoint_artifacts(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            checkpoint_path = Path(result["checkpoint_path"])
            checkpoint = yaml.safe_load(checkpoint_path.read_text(encoding="utf-8"))
            checkpoint["state"]["input_artifacts"] = None
            checkpoint_path.write_text(yaml.safe_dump(checkpoint, sort_keys=False), encoding="utf-8")
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=malformed_checkpoint_artifacts):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")

        self.assertFalse(normal["passed"])
        self.assertIn("invalid_checkpoint_artifacts", normal["failure_reasons"])

    def test_artifact_outside_run_directory_is_rejected(self):
        from run_evals import run_scenario as real_run_scenario

        def external_artifact(*args, **kwargs):
            result = real_run_scenario(*args, **kwargs)
            external = Path(result["trace_path"]).parent.parent / "external.txt"
            external.write_text("outside run", encoding="utf-8")
            result["artifacts"][0] = {
                "ref": result["artifacts"][0]["ref"],
                "path": str(external),
                "hash": "sha256:" + __import__("hashlib").sha256(external.read_bytes()).hexdigest(),
            }
            return result

        with tempfile.TemporaryDirectory() as temp, patch("run_evals.run_scenario", side_effect=external_artifact):
            report = run_cases(CASES_PATH, Path(temp))
            normal = next(item for item in report["cases"] if item["category"] == "normal")

        self.assertFalse(normal["passed"])
        self.assertIn("artifact_outside_run_dir", normal["failure_reasons"])

    def test_declared_artifact_hash_mismatch_is_rejected(self):
        cases = yaml.safe_load(CASES_PATH.read_text(encoding="utf-8"))
        cases[0]["artifacts"][0]["hash"] = "sha256:" + ("0" * 64)
        with tempfile.TemporaryDirectory() as temp:
            cases_path = Path(temp) / "cases.yaml"
            cases_path.write_text(yaml.safe_dump(cases, sort_keys=False), encoding="utf-8")
            report = run_cases(cases_path, Path(temp) / "out")

        normal = next(item for item in report["cases"] if item["category"] == "normal")
        self.assertFalse(normal["passed"])
        self.assertIn("artifact_hash_mismatch_expected:patch.diff", normal["failure_reasons"])


if __name__ == "__main__":
    unittest.main()
