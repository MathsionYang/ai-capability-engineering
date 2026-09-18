import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


RUNNER_DIR = Path(__file__).parents[1]
sys.path.insert(0, str(RUNNER_DIR))

from runner import CheckpointStore, FIXTURE_DIR, TraceWriter, run_scenario  # noqa: E402


class RunnerContractTest(unittest.TestCase):
    def test_fixture_contains_search_targets(self):
        self.assertTrue((FIXTURE_DIR / "src" / "total.py").exists())
        self.assertTrue((FIXTURE_DIR / "tests" / "test_total.py").exists())

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
                self.assertEqual(event["span_id"], run_dir.name + "-span-001")
            self.assertTrue(any(event.get("output_ref", "").startswith("artifact://") for event in events))
            self.assertIn("artifact", event_types)
            for event in events:
                ref = event.get("output_ref", "")
                if not ref.startswith(f"artifact://runs/{run_dir.name}/"):
                    continue
                artifact_path = run_dir / ref.rsplit("/", 1)[-1]
                self.assertTrue(artifact_path.exists(), event["output_ref"])
                expected_hash = "sha256:" + hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                self.assertEqual(event.get("artifact_hash"), expected_hash)
                self.assertEqual(event.get("output_hash"), expected_hash)

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
                events = [json.loads(line) for line in Path(result["trace_path"]).read_text().splitlines()]
                final = [event for event in events if event["event_type"] == "final_output"][-1]
                self.assertTrue(final.get("output_ref", "").startswith("artifact://"))
                if scenario == "tool-timeout":
                    failed = [event for event in events if event["status"] == "failed" and event["event_type"] == "observation"]
                    self.assertTrue(failed)
                    self.assertTrue(all(event.get("duration_ms") == 12 for event in failed))

    def test_checkpoint_store_round_trips_state(self):
        with tempfile.TemporaryDirectory() as temp:
            store = CheckpointStore(Path(temp) / "checkpoint.yaml")
            state = {"task_id": "task-1", "status": "working", "cursor": {"step_id": "search_repo", "step_index": 1, "completed_steps": []}, "resume_policy": {"idempotency_key": "task-1:search:1"}, "state": {}, "failure": {"code": None, "message": None, "retryable": False, "failed_at": None}, "owner": {"agent_id": "code-repair-agent", "graph_version": "v1"}}
            path = store.save(state)
            self.assertEqual(store.load(), state)
            self.assertEqual(path, Path(temp) / "checkpoint.yaml")

    def test_duplicate_replay_does_not_apply_patch_twice(self):
        with tempfile.TemporaryDirectory() as temp:
            first = run_scenario("duplicate-replay", Path(temp))
            second = run_scenario("duplicate-replay", Path(temp))
            self.assertEqual(first["status"], "completed")
            self.assertEqual(first["failure_class"], "duplicate_execution")
            self.assertEqual(first["side_effect_count"], 1)
            self.assertEqual(second["side_effect_count"], 0)
            self.assertEqual(second["run_id"], first["run_id"])
            self.assertTrue(any(item["ref"].endswith("patch.diff") for item in second["artifacts"]))

    def test_resume_from_completed_checkpoint_reuses_run_without_side_effect(self):
        with tempfile.TemporaryDirectory() as temp:
            first = run_scenario("success", Path(temp))
            resumed = run_scenario("success", Path(temp), resume_from=Path(first["checkpoint_path"]))
            self.assertEqual(resumed["run_id"], first["run_id"])
            self.assertEqual(resumed["status"], "completed")
            self.assertEqual(resumed["side_effect_count"], 0)

    def test_checkpoint_contains_artifact_and_retry_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run_scenario("tool-timeout", Path(temp))
            checkpoint = CheckpointStore(Path(result["checkpoint_path"])).load()
            state = checkpoint["state"]
            self.assertIn("input_artifacts", state)
            self.assertIn("output_artifacts", state)
            self.assertIn("side_effect_log", state)
            self.assertIn("retry_count", state)

    def test_trace_and_checkpoint_helpers_produce_files(self):
        with tempfile.TemporaryDirectory() as temp:
            trace = TraceWriter(Path(temp) / "trace.jsonl", "trace-1", "task-1")
            event = trace.emit("goal", "receive_goal", "succeeded")
            trace.close()
            self.assertEqual(event["event_type"], "goal")
            self.assertEqual(len((Path(temp) / "trace.jsonl").read_text().splitlines()), 1)

    def test_trace_writer_rejects_canonical_field_override(self):
        with tempfile.TemporaryDirectory() as temp:
            trace = TraceWriter(Path(temp) / "trace.jsonl", "trace-1", "task-1")
            with self.assertRaises(ValueError):
                trace.emit("goal", "receive_goal", "succeeded", trace_id="spoofed")
            trace.close()

    def test_permission_denied_records_real_human_review_event(self):
        with tempfile.TemporaryDirectory() as temp:
            result = run_scenario("permission-denied", Path(temp))
            events = [json.loads(line) for line in Path(result["trace_path"]).read_text().splitlines()]
            confirmations = [event for event in events if event["event_type"] == "human_confirmation"]
            self.assertTrue(confirmations)
            self.assertEqual(confirmations[-1]["status"], "waiting")
            self.assertEqual(confirmations[-1].get("decision"), "blocked")
            patch_events = [event for event in events if event["name"] == "apply_patch"]
            self.assertTrue(patch_events)
            self.assertTrue(all(event["status"] == "skipped" for event in patch_events))


if __name__ == "__main__":
    unittest.main()
