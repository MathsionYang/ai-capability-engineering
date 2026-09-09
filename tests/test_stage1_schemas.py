import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).parents[1]
SCHEMA_DIR = ROOT / "cn" / "assets" / "schemas"
CHECKLIST_DIR = ROOT / "cn" / "assets" / "checklists"


class Stage1SchemasTest(unittest.TestCase):
    def test_trace_schema_defines_hierarchy_order_failure_and_redaction(self):
        document = (SCHEMA_DIR / "trace-event.md").read_text(encoding="utf-8")

        for term in ("Trace", "Span", "Event", "event_type", "sequence", "failure_class", "redact", "parent_event_id"):
            self.assertIn(term, document)

        for field in ("trace_id", "event_id", "task_id", "timestamp", "event_type", "name", "status"):
            self.assertIn(f"`{field}`", document)
        self.assertIn("human_confirmation", document)
        self.assertIn("waiting", document)
        self.assertIn("artifact://", document)
        self.assertIn("artifact_hash", document)
        self.assertIn("sha256:", document)

        match = re.search(r"```yaml\s+(.*?)\s+```", document, flags=re.DOTALL)
        self.assertIsNotNone(match, "trace schema must include a YAML example")
        example = yaml.safe_load(match.group(1))
        event = example["trace"]["spans"][0]["events"][0]
        self.assertTrue({"trace_id", "event_id", "task_id", "timestamp", "event_type", "name", "status"}.issubset(event))
        self.assertEqual(example["trace"]["spans"][0]["events"][0]["event_type"], "goal")
        self.assertIn("parent_event_id", example["trace"]["spans"][0]["events"][1])

    def test_checkpoint_schema_has_resume_contract_and_allowed_statuses(self):
        schema = yaml.safe_load((SCHEMA_DIR / "checkpoint-state.yaml").read_text(encoding="utf-8"))
        required = {"task_id", "status", "cursor", "resume_policy", "state", "failure", "owner"}
        self.assertTrue(required.issubset(schema["schema"]["required"]))
        self.assertEqual(schema["schema"]["properties"]["resume_policy"]["required"], ["idempotency_key"])
        self.assertEqual(schema["schema"]["properties"]["status"]["enum"], ["submitted", "working", "validating", "retrying", "input-required", "waiting-confirmation", "completed", "failed", "cancelled"])
        self.assertIn("permission_denied", schema["schema"]["properties"]["failure"]["properties"]["code"]["enum"])
        self.assertIn("checkpoint_id", schema["example"])

    def test_eval_schema_has_execution_evidence_and_fixture_contract(self):
        schema = yaml.safe_load((SCHEMA_DIR / "eval-case.yaml").read_text(encoding="utf-8"))
        required = {
            "case_id", "category", "scenario", "input", "expected", "forbidden_actions",
            "required_evidence", "artifacts", "rubric", "fixtures",
        }
        self.assertTrue(required.issubset(schema["schema"]["required"]))
        self.assertEqual(schema["schema"]["properties"]["category"]["enum"], ["normal", "input_incomplete", "tool_failure", "high_risk", "historical_regression"])
        self.assertIn("category", schema["example"])
        self.assertIn(schema["example"]["category"], schema["schema"]["properties"]["category"]["enum"])
        self.assertIn("required_evidence", schema["example"])
        self.assertIn("fixtures", schema["example"])
        self.assertTrue(schema["example"]["rubric"])
        self.assertTrue(all(item["ref"].startswith("artifact://") and item["hash"].startswith("sha256:") for item in schema["example"]["artifacts"]))
        self.assertTrue(all(item["ref"].startswith("artifact://") and item["hash"].startswith("sha256:") for item in schema["example"]["input"]["artifacts"]))
        self.assertEqual(schema["schema"]["properties"]["artifacts"]["items"]["required"], ["ref", "hash"])

    def test_validator_decision_covers_required_paths(self):
        document = (CHECKLIST_DIR / "validator-decision.md").read_text(encoding="utf-8")
        for path in ("输入不完整", "工具超时", "验证失败", "权限拒绝", "重复执行"):
            self.assertIn(path, document)
        for term in ("观测信号", "处理策略", "恢复点", "回流 Eval"):
            self.assertIn(term, document)

    def test_regression_report_has_gates_and_attribution(self):
        document = (CHECKLIST_DIR / "regression-report.md").read_text(encoding="utf-8")
        for term in ("基线", "失败归因", "成本", "延迟", "门禁", "回流 Eval"):
            self.assertIn(term, document)


if __name__ == "__main__":
    unittest.main()
