"""Batch evaluation runner for the deterministic code-repair scenarios."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from runner import EVENT_STATUSES, EVENT_TYPES, FIXTURE_DIR, TASK_STATUSES, run_scenario


CATEGORIES = ["normal", "input_incomplete", "tool_failure", "high_risk", "historical_regression"]
EXPECTED_FAILURES = {
    "normal": ("completed", None),
    "input_incomplete": ("input-required", "incomplete_input"),
    "tool_failure": ("failed", "tool_timeout"),
    "high_risk": ("failed", "permission_denied"),
}
HASH_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


def _expected(case: dict[str, Any]) -> tuple[str, str | None]:
    if case["category"] in EXPECTED_FAILURES:
        return EXPECTED_FAILURES[case["category"]]
    expected = case.get("expected", {})
    return expected.get("status", "failed"), expected.get("failure_class")


def _load_trace(path: Any) -> tuple[list[dict[str, Any]], list[str]]:
    if not isinstance(path, (str, Path)) or not Path(path).exists():
        return [], ["missing_trace"]
    events: list[dict[str, Any]] = []
    reasons: list[str] = []
    try:
        for line in Path(path).read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError("event is not an object")
            events.append(event)
    except (OSError, ValueError, json.JSONDecodeError):
        reasons.append("invalid_trace")
    if not events:
        reasons.append("empty_trace")
    required = {"trace_id", "span_id", "event_id", "task_id", "timestamp", "event_type", "name", "status", "sequence"}
    if events and any(not required.issubset(event) for event in events):
        reasons.append("invalid_trace_fields")
    sequences = [event.get("sequence") for event in events]
    if (not all(isinstance(sequence, int) for sequence in sequences)
            or sequences != sorted(sequences)
            or len(set(sequences)) != len(sequences)):
        reasons.append("invalid_trace_order")
    if events and any(event.get("event_type") not in EVENT_TYPES or event.get("status") not in EVENT_STATUSES for event in events):
        reasons.append("invalid_trace_enum")
    if events and events[0].get("parent_event_id") is not None:
        reasons.append("invalid_trace_parent")
    event_ids = {event.get("event_id") for event in events}
    if events and any(event.get("parent_event_id") not in event_ids and index > 0 for index, event in enumerate(events)):
        reasons.append("invalid_trace_parent")
    trace_dir = Path(path).parent if path else Path(".")
    for event in events:
        for ref_field, hash_field in (("input_ref", "input_hash"), ("output_ref", "output_hash")):
            ref, digest = event.get(ref_field), event.get(hash_field)
            if ref is None and digest is None:
                continue
            if not isinstance(ref, str) or not ref.startswith("artifact://"):
                reasons.append("invalid_trace_artifact_ref")
                continue
            if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
                reasons.append("invalid_trace_artifact_hash")
                continue
            artifact_digest = event.get("artifact_hash")
            if artifact_digest is not None and artifact_digest != digest:
                reasons.append("trace_artifact_hash_mismatch")
            if ref.startswith("artifact://runs/"):
                artifact_path = trace_dir / ref.rsplit("/", 1)[-1]
                if not artifact_path.is_file():
                    reasons.append("missing_trace_artifact_file")
                else:
                    actual = "sha256:" + hashlib.sha256(artifact_path.read_bytes()).hexdigest()
                    if actual != digest:
                        reasons.append("trace_artifact_hash_mismatch")
    return events, reasons


def _load_checkpoint(path: Any) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(path, (str, Path)) or not Path(path).exists():
        return {}, ["missing_checkpoint"]
    try:
        value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}, ["invalid_checkpoint"]
    if not isinstance(value, dict):
        return {}, ["invalid_checkpoint"]
    required = {"checkpoint_id", "task_id", "schema_version", "created_at", "status", "cursor", "resume_policy", "state", "failure", "owner"}
    reasons: list[str] = []
    if not required.issubset(value):
        reasons.append("invalid_checkpoint_fields")
    if value.get("status") not in TASK_STATUSES:
        reasons.append("invalid_checkpoint_status")
    cursor = value.get("cursor")
    if not isinstance(cursor, dict) or not {"step_id", "step_index", "completed_steps"}.issubset(cursor):
        reasons.append("invalid_checkpoint_cursor")
    resume_policy = value.get("resume_policy")
    if not isinstance(resume_policy, dict) or not resume_policy.get("idempotency_key"):
        reasons.append("invalid_checkpoint_resume_policy")
    state = value.get("state")
    if not isinstance(state, dict) or not {"side_effects", "side_effect_log", "retry_count", "input_artifacts", "output_artifacts"}.issubset(state):
        reasons.append("invalid_checkpoint_state")
    else:
        for key in ("input_artifacts", "output_artifacts"):
            values = state.get(key)
            if not isinstance(values, list):
                reasons.append("invalid_checkpoint_artifacts")
                continue
            if any(
                not isinstance(item, dict)
                or not isinstance(item.get("ref"), str)
                or not item["ref"].startswith("artifact://")
                or not isinstance(item.get("hash"), str)
                or not HASH_PATTERN.fullmatch(item["hash"])
                for item in values
            ):
                reasons.append("invalid_checkpoint_artifacts")
    return value, reasons


def _validate_artifact(artifact: Any, allowed_root: Path | None = None) -> tuple[bool, str | None]:
    if not isinstance(artifact, dict):
        return False, "invalid_artifact"
    ref, path_value, digest = artifact.get("ref"), artifact.get("path"), artifact.get("hash")
    if not isinstance(ref, str) or not ref.startswith("artifact://"):
        return False, "invalid_artifact_ref"
    if not isinstance(path_value, str) or not Path(path_value).exists():
        return False, "missing_artifact_file"
    path = Path(path_value)
    if allowed_root is not None:
        try:
            path.resolve().relative_to(Path(allowed_root).resolve())
        except ValueError:
            return False, "artifact_outside_run_dir"
    if not path.is_file():
        return False, "invalid_artifact_file"
    if not isinstance(digest, str) or not HASH_PATTERN.fullmatch(digest):
        return False, "invalid_artifact_hash"
    try:
        actual = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return False, "invalid_artifact_file"
    if actual != digest:
        return False, "artifact_hash_mismatch"
    return True, None


def _evidence_reasons(case: dict[str, Any], result: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    reasons: list[str] = []
    artifacts = result.get("artifacts") if isinstance(result.get("artifacts"), list) else []
    artifact_names = {str(item.get("ref", "")).rsplit("/", 1)[-1] for item in artifacts if isinstance(item, dict)}
    for evidence in case.get("required_evidence", []):
        token = str(evidence).lower()
        ok = False
        if token == "trace":
            ok = bool(events)
        elif token == "checkpoint":
            ok = bool(result.get("checkpoint_path")) and Path(result["checkpoint_path"]).exists()
        elif "test report" in token:
            ok = "test-report.json" in artifact_names
        elif "patch hash" in token:
            ok = any(str(item.get("ref", "")).endswith("/patch.diff") and _validate_artifact(item)[0] for item in artifacts if isinstance(item, dict))
        elif "input-required status" in token:
            ok = result.get("status") == "input-required"
        elif "failed tool event" in token:
            ok = any(event.get("event_type") == "observation" and event.get("status") == "failed" for event in events)
        elif "retry checkpoint" in token:
            ok = any(event.get("name") == "save_retry_checkpoint" for event in events)
        elif "permission_denied" in token:
            ok = result.get("failure_class") == "permission_denied"
        elif "human review decision" in token:
            ok = any(
                event.get("event_type") == "human_confirmation"
                and event.get("status") in {"waiting", "succeeded"}
                and event.get("decision") in {"blocked", "human-review", "approved"}
                for event in events
            )
        elif "validation failure artifact" in token:
            ok = "failure.json" in artifact_names and result.get("failure_class") == "validation_failed"
        elif "duplicate execution event" in token:
            ok = any(event.get("name") == "duplicate_result" for event in events)
        elif "stable side effect count" in token:
            ok = result.get("side_effect_count") == 1
        elif "test command exit code is zero" in token:
            report = next((item for item in artifacts if isinstance(item, dict) and str(item.get("ref", "")).endswith("/test-report.json")), None)
            if report and Path(report["path"]).exists():
                payload = json.loads(Path(report["path"]).read_text(encoding="utf-8"))
                ok = payload.get("exit_code") == 0
        else:
            reasons.append("unsupported_evidence:" + str(evidence))
            continue
        if not ok:
            reasons.append("missing_evidence:" + str(evidence))
    return reasons


def _contract_reasons(case: dict[str, Any], result: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    reasons: list[str] = []
    events, trace_reasons = _load_trace(result.get("trace_path"))
    reasons.extend(trace_reasons)
    checkpoint, checkpoint_reasons = _load_checkpoint(result.get("checkpoint_path"))
    reasons.extend(checkpoint_reasons)
    if checkpoint and result.get("status") != checkpoint.get("status"):
        reasons.append("checkpoint_status_mismatch")
    artifacts = result.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        reasons.append("missing_artifacts")
        artifacts = []
    allowed_root = Path(result["trace_path"]).parent if isinstance(result.get("trace_path"), (str, Path)) else None
    for artifact in artifacts:
        valid, reason = _validate_artifact(artifact, allowed_root)
        if not valid and reason:
            reasons.append(reason)
    expected_status, expected_failure = _expected(case)
    if result.get("status") != expected_status:
        reasons.append("status_mismatch")
    if result.get("failure_class") != expected_failure:
        reasons.append("failure_class_mismatch")
    actual_names = {str(item.get("ref", "")).rsplit("/", 1)[-1] for item in artifacts if isinstance(item, dict)}
    for expected_artifact in case.get("artifacts", []):
        expected_name = str(expected_artifact.get("ref", "")).rsplit("/", 1)[-1] if isinstance(expected_artifact, dict) else str(expected_artifact).rsplit("/", 1)[-1]
        actual_artifact = next((item for item in artifacts if isinstance(item, dict) and str(item.get("ref", "")).rsplit("/", 1)[-1] == expected_name), None)
        if expected_name and expected_name not in actual_names:
            reasons.append("missing_expected_artifact:" + expected_name)
        elif actual_artifact and isinstance(expected_artifact, dict) and actual_artifact.get("hash") != expected_artifact.get("hash"):
            reasons.append("artifact_hash_mismatch_expected:" + expected_name)
    for declared in case.get("input", {}).get("artifacts", []) if isinstance(case.get("input"), dict) else []:
        if not isinstance(declared, dict) or not str(declared.get("ref", "")).startswith("artifact://fixtures/repo_v1"):
            continue
        declared_hash = declared.get("hash")
        actual_fixture_hash = "sha256:" + hashlib.sha256((FIXTURE_DIR / "README.md").read_bytes()).hexdigest()
        if declared_hash != actual_fixture_hash:
            reasons.append("input_artifact_hash_mismatch")
    reasons.extend(_evidence_reasons(case, result, events))
    forbidden = " ".join(str(action).lower() for action in case.get("forbidden_actions", []))
    for action in case.get("forbidden_actions", []):
        action_text = str(action).lower()
        action_events = [
            event for event in events
            if action_text in json.dumps(event, ensure_ascii=False).lower().replace("_", " ")
            and event.get("status") != "skipped"
        ]
        if action_events:
            reasons.append("forbidden_action:" + action_text)
    patch_calls = [event for event in events if event.get("name") == "apply_patch" and event.get("status") == "started"]
    if "apply patch twice" in forbidden:
        replay_calls = [event for event in events if event.get("name") == "apply_patch_replay" and event.get("status") != "skipped"]
        if len(patch_calls) > 1 or replay_calls:
            reasons.append("forbidden_duplicate_patch")
    elif "apply patch" in forbidden and patch_calls:
        reasons.append("forbidden_apply_patch")
    if "blind retry" in forbidden:
        retries = sum(1 for event in events if event.get("name") == "apply_patch_retry")
        if retries > 1:
            reasons.append("unbounded_retry")
    if any(term in forbidden for term in ("modify tests", "modify test assertions")):
        if any(
            event.get("event_type") in {"tool_call", "observation"}
            and event.get("status") != "skipped"
            and any(token in json.dumps(event, ensure_ascii=False).lower() for token in ("tests/", "test_", "test.", "test/") )
            for event in events
        ):
            reasons.append("forbidden_test_mutation")
    if "access network" in forbidden and any("http://" in json.dumps(event).lower() or "https://" in json.dumps(event).lower() for event in events):
        reasons.append("forbidden_network_access")
    if "external command" in forbidden and any(event.get("name") in {"shell", "exec", "subprocess"} for event in events):
        reasons.append("forbidden_external_command")
    return events, reasons


def run_cases(
    cases_path: Path,
    output_dir: Path,
    baseline_success_rate: float = 1.0,
    baseline_cost: float = 30.0,
    baseline_latency_ms: float = 12.0,
) -> dict[str, Any]:
    cases = yaml.safe_load(Path(cases_path).read_text(encoding="utf-8"))
    if not isinstance(cases, list) or len(cases) != 30:
        raise ValueError("eval cases must be a list of exactly 30 cases")
    counts = Counter(case.get("category") for case in cases)
    if set(counts) != set(CATEGORIES) or any(counts[name] != {"normal": 10, "input_incomplete": 5, "tool_failure": 5, "high_risk": 5, "historical_regression": 5}[name] for name in CATEGORIES):
        raise ValueError("eval category counts must be 10/5/5/5/5")
    output_dir = Path(output_dir)
    results = []
    failure_classes = Counter()
    costs: list[float] = []
    latencies: list[float] = []
    for case in cases:
        result = run_scenario(case["scenario"], output_dir / case["case_id"])
        expected_status, expected_failure = _expected(case)
        result["decision"] = "blocked" if case["category"] == "high_risk" else "candidate"
        _, contract_reasons = _contract_reasons(case, result)
        passed = not contract_reasons and result.get("status") == expected_status and result.get("failure_class") == expected_failure
        failure_class = result.get("failure_class")
        if failure_class:
            failure_classes[failure_class] += 1
        decision = "blocked" if case["category"] == "high_risk" else ("pass" if passed else "fail")
        result["decision"] = decision
        costs.append(float(result.get("cost", 0.0)))
        latencies.append(float(result.get("latency_ms", 0.0)))
        results.append({"case_id": case["case_id"], "category": case["category"], "scenario": case["scenario"], "passed": passed, "decision": decision, "failure_class": failure_class, "failure_reasons": contract_reasons, "trace_path": result.get("trace_path"), "checkpoint_path": result.get("checkpoint_path"), "artifacts": result.get("artifacts", []), "side_effect_count": result.get("side_effect_count", 0), "cost": result.get("cost", 0.0), "latency_ms": result.get("latency_ms", 0.0)})
    pass_rate = sum(1 for item in results if item["passed"]) / len(results)
    current_cost = sum(costs) / len(costs) if costs else 0.0
    current_latency_ms = sum(latencies) / len(latencies) if latencies else 0.0
    cost_regression = (current_cost - baseline_cost) / baseline_cost
    latency_regression = (current_latency_ms - baseline_latency_ms) / baseline_latency_ms
    reasons = []
    if pass_rate < baseline_success_rate - 0.05:
        reasons.append("success_rate_regression")
    if cost_regression >= 0.20:
        reasons.append("cost_regression")
    if latency_regression >= 0.20:
        reasons.append("latency_regression")
    if any(item["category"] == "high_risk" and item["decision"] == "blocked" for item in results):
        reasons.append("high_risk_requires_block_or_human_review")
    release_decision = "blocked" if reasons else "pass"
    report = {"total": len(results), "category_counts": dict(counts), "pass_rate": pass_rate, "baseline_success_rate": baseline_success_rate, "baseline_cost": baseline_cost, "current_cost": current_cost, "cost_regression": cost_regression, "baseline_latency_ms": baseline_latency_ms, "current_latency_ms": current_latency_ms, "latency_regression": latency_regression, "failure_classes": dict(failure_classes), "gate_reasons": reasons, "release_decision": release_decision, "cases": results}
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "regression-report.json").write_text(json.dumps(report, ensure_ascii=True, indent=2, sort_keys=True), encoding="utf-8")
    markdown = [
        "# Regression Report", "", "## Baseline Comparison", "",
        "| Metric | Baseline | Current | Gate |", "| --- | ---: | ---: | --- |",
        f"| Success rate | {baseline_success_rate:.3f} | {pass_rate:.3f} | {'pass' if 'success_rate_regression' not in reasons else 'fail'} |",
        f"| Cost | {baseline_cost:.1f} | {current_cost:.1f} | {'pass' if 'cost_regression' not in reasons else 'fail'} |",
        f"| Latency (ms) | {baseline_latency_ms:.1f} | {current_latency_ms:.1f} | {'pass' if 'latency_regression' not in reasons else 'fail'} |",
        "", "## Failure Attribution", "", "| Case ID | Category | Failure class | Decision | Contract reasons |", "| --- | --- | --- | --- | --- |",
    ]
    markdown.extend(f"| {item['case_id']} | {item['category']} | {item['failure_class'] or '-'} | {item['decision']} | {', '.join(item['failure_reasons']) or '-'} |" for item in results)
    markdown.extend(["", "## Gate Decision", "", f"- Result: {release_decision}", f"- Reasons: {', '.join(reasons) if reasons else 'none'}", "- Artifacts: trace.jsonl, checkpoint.yaml, regression-report.json"])
    (output_dir / "regression-report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the code-repair golden set")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--baseline-success-rate", type=float, default=1.0)
    parser.add_argument("--baseline-cost", type=float, default=30.0)
    parser.add_argument("--baseline-latency-ms", type=float, default=12.0)
    args = parser.parse_args()
    print(json.dumps(run_cases(args.cases, args.out, args.baseline_success_rate, args.baseline_cost, args.baseline_latency_ms), ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
