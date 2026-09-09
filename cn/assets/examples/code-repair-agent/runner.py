"""Deterministic, offline code-repair execution loop used by Stage 1."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml


EVENT_TYPES = {
    "goal", "plan", "tool_call", "observation", "validation", "checkpoint",
    "artifact", "human_confirmation", "final_output",
}
EVENT_STATUSES = {"started", "succeeded", "failed", "skipped", "waiting"}
TASK_STATUSES = {
    "submitted", "working", "validating", "retrying", "input-required",
    "waiting-confirmation", "completed", "failed", "cancelled",
}
SCENARIOS = {
    "success", "input-required", "tool-timeout", "validation-failed",
    "permission-denied", "duplicate-replay",
}
FIXED_TIMESTAMP = "2026-09-09T00:00:00+00:00"
FIXTURE_DIR = Path(__file__).parent / "fixtures" / "repo_v1"


def _sha256(value: str | bytes) -> str:
    data = value.encode("utf-8") if isinstance(value, str) else value
    return "sha256:" + hashlib.sha256(data).hexdigest()


class TraceWriter:
    """Write canonical JSONL events with stable identifiers and ordering."""

    def __init__(self, path: Path, trace_id: str, task_id: str, span_id: str | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trace_id = trace_id
        self.task_id = task_id
        self.span_id = span_id or f"{trace_id}-span-001"
        self._sequence = 0
        self._last_event_id: str | None = None
        self._handle = self.path.open("w", encoding="utf-8", newline="\n")

    def emit(self, event_type: str, name: str, status: str, **fields: Any) -> dict[str, Any]:
        if event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {event_type}")
        if status not in EVENT_STATUSES:
            raise ValueError(f"unsupported event status: {status}")
        protected = {"trace_id", "span_id", "event_id", "task_id", "timestamp", "sequence"}
        if protected.intersection(fields):
            raise ValueError("canonical trace fields cannot be overridden")
        self._sequence += 1
        event_id = f"{self.trace_id}-ev-{self._sequence:03d}"
        event = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "event_id": event_id,
            "parent_event_id": fields.pop("parent_event_id", self._last_event_id),
            "task_id": self.task_id,
            "timestamp": FIXED_TIMESTAMP,
            "sequence": self._sequence,
            "event_type": event_type,
            "name": name,
            "status": status,
        }
        event.update(fields)
        self._handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")
        self._handle.flush()
        self._last_event_id = event_id
        return event

    def close(self) -> None:
        self._handle.close()

    def __enter__(self) -> "TraceWriter":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


class CheckpointStore:
    def __init__(self, path: Path):
        self.path = Path(path)

    def save(self, state: dict[str, Any]) -> Path:
        status = state.get("status")
        if status not in TASK_STATUSES:
            raise ValueError(f"unsupported task status: {status}")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(yaml.safe_dump(state, sort_keys=False, allow_unicode=False), encoding="utf-8")
        return self.path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        value = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}


def search_repo(query: str = "failing test") -> dict[str, Any]:
    content = (FIXTURE_DIR / "README.md").read_text(encoding="utf-8")
    return {"query": query, "matches": ["src/total.py", "tests/test_total.py"], "fixture_hash": _sha256(content)}


def run_tests(patched: bool = True) -> dict[str, Any]:
    return {"command": "python -m unittest tests/test_total.py", "exit_code": 0 if patched else 1, "duration_ms": 12}


def apply_patch() -> dict[str, Any]:
    return {"path": "src/total.py", "changed": True, "patch": "- return a - b\n+ return a + b\n"}


def git_diff() -> str:
    return "diff --git a/src/total.py b/src/total.py\n--- a/src/total.py\n+++ b/src/total.py\n@@\n-return a - b\n+return a + b\n"


def _artifact(run_id: str, run_dir: Path, name: str, content: str) -> dict[str, str]:
    path = run_dir / name
    data = content.encode("utf-8")
    path.write_bytes(data)
    digest = _sha256(data)
    return {"ref": f"artifact://runs/{run_id}/{name}", "path": str(path), "hash": digest}


def _emit_artifact(trace: TraceWriter, artifact: dict[str, str], name: str) -> None:
    trace.emit(
        "artifact",
        name,
        "succeeded",
        output_ref=artifact["ref"],
        output_hash=artifact["hash"],
        artifact_hash=artifact["hash"],
    )


def _checkpoint(
    run_id: str,
    store: CheckpointStore,
    status: str,
    step_id: str,
    index: int,
    completed: list[str],
    side_effects: int,
    failure_class: str | None = None,
    *,
    input_artifacts: list[dict[str, str]] | None = None,
    output_artifacts: list[dict[str, str]] | None = None,
    retry_count: int = 0,
    side_effect_log: list[str] | None = None,
) -> dict[str, Any]:
    fixture_path = FIXTURE_DIR / "README.md"
    fixture_artifact = {
        "ref": "artifact://fixtures/repo_v1/README.md",
        "hash": _sha256(fixture_path.read_bytes()),
    }
    state = {
        "checkpoint_id": f"{run_id}-cp-{index:03d}",
        "task_id": run_id,
        "schema_version": 1,
        "created_at": FIXED_TIMESTAMP,
        "status": status,
        "cursor": {"step_id": step_id, "step_index": index, "completed_steps": completed},
        "resume_policy": {"idempotency_key": f"{run_id}:{step_id}:1", "replay_mode": "deterministic", "max_retries": 1},
        "state": {
            "side_effects": side_effects,
            "side_effect_log": list(side_effect_log or ([] if side_effects == 0 else ["apply_patch"])),
            "retry_count": retry_count,
            "fixture": "repo_v1",
            "input_artifacts": list(input_artifacts or [fixture_artifact]),
            "output_artifacts": list(output_artifacts or []),
        },
        "failure": {"code": failure_class, "message": failure_class, "retryable": failure_class == "tool_timeout", "failed_at": FIXED_TIMESTAMP if failure_class else None},
        "owner": {"agent_id": "code-repair-agent", "graph_version": "v1"},
    }
    store.save(state)
    return state


def _next_run_id(output_dir: Path, scenario: str) -> str:
    root = output_dir / "artifacts"
    root.mkdir(parents=True, exist_ok=True)
    prefix = f"run-{scenario}-"
    numbers = []
    for path in root.glob(prefix + "*"):
        suffix = path.name[len(prefix):]
        if suffix.isdigit():
            numbers.append(int(suffix))
    return f"{prefix}{max(numbers, default=0) + 1:03d}"


def _cached_duplicate(output_dir: Path) -> dict[str, Any] | None:
    root = output_dir / "artifacts"
    candidates = sorted(root.glob("run-duplicate-replay-*")) if root.exists() else []
    if not candidates:
        return None
    run_dir = candidates[-1]
    run_id = run_dir.name
    artifacts = []
    for path in sorted(run_dir.iterdir()):
        if path.name not in {"trace.jsonl", "checkpoint.yaml"}:
            artifacts.append({"ref": f"artifact://runs/{run_id}/{path.name}", "path": str(path), "hash": _sha256(path.read_bytes())})
    return {
        "run_id": run_id,
        "status": "completed",
        "failure_class": "duplicate_execution",
        "artifacts": artifacts,
        "trace_path": str(run_dir / "trace.jsonl"),
        "checkpoint_path": str(run_dir / "checkpoint.yaml"),
        "side_effect_count": 0,
        "cost": 30.0,
        "latency_ms": 12.0,
    }


def _result_from_run_dir(run_dir: Path, side_effect_count: int = 0) -> dict[str, Any]:
    run_dir = Path(run_dir)
    run_id = run_dir.name
    checkpoint = CheckpointStore(run_dir / "checkpoint.yaml").load()
    failure_class = (checkpoint.get("failure") or {}).get("code")
    artifacts = []
    for path in sorted(run_dir.iterdir()):
        if path.name not in {"trace.jsonl", "checkpoint.yaml"}:
            artifacts.append({"ref": f"artifact://runs/{run_id}/{path.name}", "path": str(path), "hash": _sha256(path.read_bytes())})
    return {
        "run_id": run_id,
        "status": checkpoint.get("status", "failed"),
        "failure_class": failure_class,
        "artifacts": artifacts,
        "trace_path": str(run_dir / "trace.jsonl"),
        "checkpoint_path": str(run_dir / "checkpoint.yaml"),
        "side_effect_count": side_effect_count,
        "cost": 30.0,
        "latency_ms": 12.0,
    }


def _final_artifact_fields(artifacts: list[dict[str, str]]) -> dict[str, str]:
    for filename in ("test-report.json", "patch.diff", "failure.json", "goal.json"):
        artifact = next((item for item in artifacts if item["ref"].endswith("/" + filename)), None)
        if artifact:
            return {
                "output_ref": artifact["ref"],
                "output_hash": artifact["hash"],
                "artifact_hash": artifact["hash"],
            }
    return {}


def run_scenario(scenario: str, output_dir: Path, *, resume_from: Path | None = None) -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")
    output_dir = Path(output_dir)
    if resume_from is not None:
        checkpoint_path = Path(resume_from)
        if not checkpoint_path.exists():
            raise FileNotFoundError(checkpoint_path)
        run_dir = checkpoint_path.parent
        checkpoint = CheckpointStore(checkpoint_path).load()
        if checkpoint.get("status") in {"completed", "failed", "cancelled", "input-required"}:
            return _result_from_run_dir(run_dir)
    if scenario == "duplicate-replay":
        cached = _cached_duplicate(output_dir)
        if cached is not None:
            return cached
    run_id = _next_run_id(output_dir, scenario)
    run_dir = output_dir / "artifacts" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    trace_path = run_dir / "trace.jsonl"
    checkpoint_path = run_dir / "checkpoint.yaml"
    store = CheckpointStore(checkpoint_path)
    failure_class: str | None = None
    side_effects = 0
    artifacts: list[dict[str, str]] = []

    with TraceWriter(trace_path, run_id, run_id) as trace:
        goal_artifact = _artifact(run_id, run_dir, "goal.json", json.dumps({"run_id": run_id, "scenario": scenario}, sort_keys=True))
        artifacts.append(goal_artifact)
        trace.emit("goal", "receive_goal", "succeeded", output_ref=goal_artifact["ref"], output_hash=goal_artifact["hash"], artifact_hash=goal_artifact["hash"])
        trace.emit("plan", "create_repair_plan", "succeeded")
        _emit_artifact(trace, goal_artifact, "goal_artifact")
        if scenario == "input-required":
            failure_class = "incomplete_input"
            state = _checkpoint(run_id, store, "input-required", "input_received", 1, ["goal", "plan"], 0, failure_class, output_artifacts=artifacts)
            trace.emit("checkpoint", "save_checkpoint", "succeeded", checkpoint_id=state["checkpoint_id"])
            failure_artifact = _artifact(run_id, run_dir, "failure.json", json.dumps({"failure_class": failure_class}, sort_keys=True))
            artifacts.append(failure_artifact)
            _emit_artifact(trace, failure_artifact, "failure_artifact")
            trace.emit("final_output", "await_input", "waiting", failure_class=failure_class, **_final_artifact_fields(artifacts))
        elif scenario == "permission-denied":
            trace.emit("human_confirmation", "confirm_high_risk", "waiting", decision="blocked", reason="permission policy requires human review")
            trace.emit("tool_call", "apply_patch", "skipped", idempotency_key=f"{run_id}:apply_patch:1", skip_reason="human_review_required")
            failure_class = "permission_denied"
            trace.emit("observation", "apply_patch_result", "failed", failure_class=failure_class, duration_ms=12, elapsed_ms=12)
            state = _checkpoint(run_id, store, "failed", "apply_patch", 1, ["goal", "plan"], 0, failure_class, output_artifacts=artifacts)
            trace.emit("checkpoint", "save_checkpoint", "succeeded", checkpoint_id=state["checkpoint_id"])
            failure_artifact = _artifact(run_id, run_dir, "failure.json", json.dumps({"failure_class": failure_class}, sort_keys=True))
            artifacts.append(failure_artifact)
            _emit_artifact(trace, failure_artifact, "failure_artifact")
            trace.emit("final_output", "stop_for_permission", "failed", failure_class=failure_class, **_final_artifact_fields(artifacts))
        else:
            search = search_repo()
            trace.emit("tool_call", "search_repo", "started", input_ref=f"artifact://fixtures/repo_v1/README.md", input_hash=search["fixture_hash"])
            search_artifact = _artifact(run_id, run_dir, "search.json", json.dumps(search, sort_keys=True))
            artifacts.append(search_artifact)
            _emit_artifact(trace, search_artifact, "search_artifact")
            trace.emit("observation", "search_repo_result", "succeeded", output_ref=search_artifact["ref"], output_hash=search_artifact["hash"], artifact_hash=search_artifact["hash"])
            state = _checkpoint(run_id, store, "working", "apply_patch", 1, ["goal", "plan", "search_repo"], 0, output_artifacts=artifacts)
            trace.emit("checkpoint", "save_checkpoint", "succeeded", checkpoint_id=state["checkpoint_id"])
            trace.emit("tool_call", "apply_patch", "started", idempotency_key=f"{run_id}:apply_patch:1")
            if scenario == "tool-timeout":
                failure_class = "tool_timeout"
                trace.emit("observation", "apply_patch_result", "failed", failure_class=failure_class, error_code="DEADLINE_EXCEEDED", duration_ms=12, elapsed_ms=12)
                retry_state = _checkpoint(run_id, store, "retrying", "apply_patch", 2, ["goal", "plan", "search_repo"], 0, failure_class, output_artifacts=artifacts, retry_count=1)
                trace.emit("checkpoint", "save_retry_checkpoint", "succeeded", checkpoint_id=retry_state["checkpoint_id"])
                trace.emit("tool_call", "apply_patch_retry", "started", idempotency_key=f"{run_id}:apply_patch:1", retry_count=1)
                trace.emit("observation", "apply_patch_retry_result", "failed", failure_class=failure_class, error_code="DEADLINE_EXCEEDED", duration_ms=12, elapsed_ms=12)
                _checkpoint(run_id, store, "failed", "apply_patch", 3, ["goal", "plan", "search_repo"], 0, failure_class, output_artifacts=artifacts, retry_count=1)
                trace.emit("checkpoint", "save_checkpoint", "succeeded", checkpoint_id=store.load()["checkpoint_id"])
                failure_artifact = _artifact(run_id, run_dir, "failure.json", json.dumps({"failure_class": failure_class}, sort_keys=True))
                artifacts.append(failure_artifact)
                _emit_artifact(trace, failure_artifact, "failure_artifact")
                trace.emit("final_output", "retry_exhausted", "failed", failure_class=failure_class, **_final_artifact_fields(artifacts))
            else:
                patch = apply_patch()
                side_effects = 1
                patch_artifact = _artifact(run_id, run_dir, "patch.diff", git_diff())
                artifacts.append(patch_artifact)
                _emit_artifact(trace, patch_artifact, "patch_artifact")
                trace.emit("observation", "apply_patch_result", "succeeded", output_ref=patch_artifact["ref"], output_hash=patch_artifact["hash"], artifact_hash=patch_artifact["hash"])
                trace.emit("tool_call", "run_tests", "started")
                test_result = run_tests(patched=scenario != "validation-failed")
                report_artifact = _artifact(run_id, run_dir, "test-report.json", json.dumps(test_result, sort_keys=True))
                artifacts.append(report_artifact)
                _emit_artifact(trace, report_artifact, "test_report_artifact")
                trace.emit("observation", "run_tests_result", "succeeded" if test_result["exit_code"] == 0 else "failed", output_ref=report_artifact["ref"], output_hash=report_artifact["hash"], artifact_hash=report_artifact["hash"], exit_code=test_result["exit_code"])
                trace.emit("validation", "validate_repair", "succeeded" if test_result["exit_code"] == 0 else "failed")
                if scenario == "validation-failed":
                    failure_class = "validation_failed"
                    final_status = "failed"
                elif scenario == "duplicate-replay":
                    failure_class = "duplicate_execution"
                    final_status = "completed"
                    trace.emit("tool_call", "apply_patch_replay", "skipped", idempotency_key=f"{run_id}:apply_patch:1")
                    trace.emit("observation", "duplicate_result", "succeeded", output_ref=patch_artifact["ref"], output_hash=patch_artifact["hash"], artifact_hash=patch_artifact["hash"])
                else:
                    final_status = "completed"
                state = _checkpoint(
                    run_id,
                    store,
                    final_status,
                    "final_output",
                    3,
                    ["goal", "plan", "search_repo", "apply_patch", "run_tests", "validation"],
                    side_effects,
                    failure_class,
                    output_artifacts=artifacts,
                )
                trace.emit("checkpoint", "save_checkpoint", "succeeded", checkpoint_id=state["checkpoint_id"])
                if failure_class:
                    failure_artifact = _artifact(run_id, run_dir, "failure.json", json.dumps({"failure_class": failure_class}, sort_keys=True))
                    artifacts.append(failure_artifact)
                    _emit_artifact(trace, failure_artifact, "failure_artifact")
                trace.emit("final_output", "return_result", "succeeded" if final_status == "completed" else "failed", failure_class=failure_class, **_final_artifact_fields(artifacts))

    return {
        "run_id": run_id,
        "status": store.load().get("status", "failed"),
        "failure_class": failure_class,
        "artifacts": artifacts,
        "trace_path": str(trace_path),
        "checkpoint_path": str(checkpoint_path),
        "side_effect_count": side_effects,
        "cost": 30.0,
        "latency_ms": 12.0,
    }
