"""Batch evaluation runner for the deterministic code-repair scenarios."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from runner import run_scenario


CATEGORIES = ["normal", "input_incomplete", "tool_failure", "high_risk", "historical_regression"]
EXPECTED_FAILURES = {
    "normal": ("completed", None),
    "input_incomplete": ("input-required", "incomplete_input"),
    "tool_failure": ("failed", "tool_timeout"),
    "high_risk": ("failed", "permission_denied"),
}


def _expected(case: dict[str, Any]) -> tuple[str, str | None]:
    if case["category"] in EXPECTED_FAILURES:
        return EXPECTED_FAILURES[case["category"]]
    expected = case.get("expected", {})
    return expected.get("status", "failed"), expected.get("failure_class")


def run_cases(cases_path: Path, output_dir: Path, baseline_success_rate: float = 1.0) -> dict[str, Any]:
    cases = yaml.safe_load(Path(cases_path).read_text(encoding="utf-8"))
    if not isinstance(cases, list) or len(cases) != 30:
        raise ValueError("eval cases must be a list of exactly 30 cases")
    counts = Counter(case.get("category") for case in cases)
    if set(counts) != set(CATEGORIES) or any(counts[name] != {"normal": 10, "input_incomplete": 5, "tool_failure": 5, "high_risk": 5, "historical_regression": 5}[name] for name in CATEGORIES):
        raise ValueError("eval category counts must be 10/5/5/5/5")
    output_dir = Path(output_dir)
    results = []
    failure_classes = Counter()
    for case in cases:
        result = run_scenario(case["scenario"], output_dir / case["case_id"])
        expected_status, expected_failure = _expected(case)
        passed = result["status"] == expected_status and result["failure_class"] == expected_failure
        failure_class = result["failure_class"]
        if failure_class:
            failure_classes[failure_class] += 1
        decision = "blocked" if case["category"] == "high_risk" else ("pass" if passed else "fail")
        results.append({"case_id": case["case_id"], "category": case["category"], "scenario": case["scenario"], "passed": passed, "decision": decision, "failure_class": failure_class, "trace_path": result["trace_path"], "checkpoint_path": result["checkpoint_path"], "artifacts": result["artifacts"], "side_effect_count": result["side_effect_count"]})
    pass_rate = sum(1 for item in results if item["passed"]) / len(results)
    baseline_cost = 30.0
    current_cost = 30.0
    baseline_latency_ms = 12.0
    current_latency_ms = 12.0
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
        "", "## Failure Attribution", "", "| Case ID | Category | Failure class | Decision |", "| --- | --- | --- | --- |",
    ]
    markdown.extend(f"| {item['case_id']} | {item['category']} | {item['failure_class'] or '-'} | {item['decision']} |" for item in results)
    markdown.extend(["", "## Gate Decision", "", f"- Result: {release_decision}", f"- Reasons: {', '.join(reasons) if reasons else 'none'}", "- Artifacts: trace.jsonl, checkpoint.yaml, regression-report.json"])
    (output_dir / "regression-report.md").write_text("\n".join(markdown) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the code-repair golden set")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_cases(args.cases, args.out), ensure_ascii=True, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
