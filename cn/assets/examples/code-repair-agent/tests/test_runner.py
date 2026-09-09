import json
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER_DIR = Path(__file__).parents[1]
sys.path.insert(0, str(RUNNER_DIR))

from runner import CheckpointStore, TraceWriter, run_scenario  # noqa: E402


class RunnerContractTest(unittest.TestCase):
    def test_success_emits_ordered_trace_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run_scenario("success", Path(temp))

            self.assertEqual(result["status"], "completed")
            self.assertIsNone(result["failure_class"])
            self.assertEqual(result["side_effect_count"], 1)
            run_dir = Path(result["trace_path"]).parent
            self.assertTrue(Path(result["trace_path"]).exists())
            self.assertTrue(Path(result["checkpoint_path"]).exists())
            self.assertTrue((run_dir / "test-report.json").exists())
            self.assertTrue((run_dir / "patch.diff").exists())

            events = [json.loads(line) for line in Path(result["trace_path"]).read_text().splitlines()]
            event_types = [event["event_type"] for event in events]
            self.assertEqual(event_types[0:2], ["goal", "plan"])
            self.assertLess(event_types.index("tool_call"), event_types.index("observation"))
            self.assertLess(event_types.index("observation"), event_types.index("validation"))
            self.assertEqual(event_types[-2:], ["checkpoint", "final_output"])
            for event in events:
                self.assertTrue({"trace_id", "event_id", "task_id", "timestamp", "event_type", "name", "status"}.issubset(event))
            self.assertTrue(any(event.get("output_ref", "").startswith("artifact://") for event in events))

    def test_failure_scenarios_stop_or_preserve_evidence(self):
        expected = {
            "input-required": ("input-required", "incomplete_input", 0),
            "tool-timeout": ("failed", "tool_timeout", 0),
            "validation-failed": ("failed", "validation_failed", 1),
            "permission-denied": ("failed", "permission_denied", 0),
        }
        with tempfile.TemporaryDirectory() as temp:
            for scenario, contract in expected.items():
                result = run_scenario(scenario, Path(temp) / scenario)
                self.assertEqual((result["status"], result["failure_class"], result["side_effect_count"]), contract)
                self.assertTrue(Path(result["trace_path"]).exists())
                self.assertTrue(Path(result["checkpoint_path"]).exists())
                self.assertTrue(result["artifacts"])

    def test_checkpoint_store_round_trips_state(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CheckpointStore(Path(temp) / "checkpoint.yaml")
            state = {"task_id": "task-1", "status": "working", "cursor": {"step_id": "search_repo", "step_index": 1, "completed_steps": []}, "resume_policy": {"idempotency_key": "task-1:search:1"}, "state": {}, "failure": {"code": None, "message": None, "retryable": False, "failed_at": None}, "owner": {"agent_id": "code-repair-agent", "graph_version": "v1"}}
            path = store.save(state)
            self.assertEqual(store.load(), state)
            self.assertEqual(path, Path(temp) / "checkpoint.yaml")

    def test_duplicate_replay_does_not_apply_patch_twice(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run_scenario("duplicate-replay", Path(temp))
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["failure_class"], "duplicate_execution")
            self.assertEqual(result["side_effect_count"], 1)
            self.assertTrue(any(item["ref"].endswith("patch.diff") for item in result["artifacts"]))

    def test_trace_and_checkpoint_helpers_produce_files(self):
        with tempfile.TemporaryDirectory() as temp:
            trace = TraceWriter(Path(temp) / "trace.jsonl", "trace-1", "task-1")
            event = trace.emit("goal", "receive_goal", "succeeded")
            trace.close()
            self.assertEqual(event["event_type"], "goal")
            self.assertEqual(len((Path(temp) / "trace.jsonl").read_text().splitlines()), 1)


if __name__ == "__main__":
    unittest.main()
